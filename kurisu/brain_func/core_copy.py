import asyncio
import inspect
import json
from datetime import datetime

from ollama import AsyncClient
from dotenv import load_dotenv

from kurisu.memory import memory_manager
from kurisu.memory import rag_engine
from kurisu.utils import ferramentas, search, think, listar_diretorio, ler_arquivo, escrever_arquivo

load_dotenv()

memory = memory_manager.load_memory()
model = "qwen3.5:9b"
MEMORY_MAX = 8
MAX_TOOL_ITERATIONS = 5  # evita loop infinito se o modelo insistir em chamar tools

_memory_lock = asyncio.Lock()


def _trim_memory():
    while len(memory) > MEMORY_MAX:
        memory.pop(0)
    while memory and memory[0].get("role") == "tool":
        memory.pop(0)


async def extract_fact(content):
    prompt = """Analise essa conversa e extraia fatos importantes e permanentes SOMENTE do usuario, e force a terceira pessoa (O usuario gosta, etc), ignore a assistente.
    Retorne APENAS um JSON assim, sem mais nada:
    {"fatos": ["fato 1", "fato 2"]}

    Responda APENAS com um objeto JSON válido. Não adicione comentários, não adicione explicações. Se a estrutura não fechar com uma chave '}', o sistema falha. Seja preciso
    Foque em: preferências, sentimentos recorrentes, eventos importantes, informações pessoais."""

    try:
        response = await AsyncClient().chat(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": str(content)}
            ],
            model=model
        )
    except Exception as e:
        print(">>> erro ao chamar o modelo em extract_fact:", e)
        return

    text = response['message']['content']
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
        new_facts = parsed["fatos"]
        memory_manager.save_facts(new_facts)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(">>> erro ao processar fatos, llm retornou:", text, "| erro:", e)


async def stream_response(messages):
    stream = await AsyncClient().chat(
        model=model,
        messages=messages,
        stream=True,
        tools=ferramentas,
        options={"temperature": 0.95},
        think=True
    )

    texto = ""
    tool_calls = []

    async for chunk in stream:
        msg = chunk.message

        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)

        if msg.content:
            texto += msg.content
            yield ("text", msg.content)

    yield ("done", {
        "content": texto,
        "tool_calls": tool_calls
    })


async def _executar_tool(tool):
    nome = tool.function.name
    args = tool.function.arguments

    if isinstance(args, str):
        args = json.loads(args)

    aviso = None
    resultado = None

    if nome == "search":
        termo = args["termo"]
        aviso = f"\n[dim #00ffff]* Pesquisando '{termo}'... *[/dim #00ffff]\n"
        resultado = search(termo)

    elif nome == "think":
        aviso = "\n[dim #ffaa00]* Analisando profundamente o problema... *[/dim #ffaa00]\n"
        resultado = think(args["prompt"])


    elif nome == "listar_diretorio":
        caminho = args["caminho"]
        aviso = f"\n[dim #ffaa00]* Listando diretório '{caminho}'... *[/dim #ffaa00]\n"
        resultado = listar_diretorio(caminho)


    elif nome == "ler_arquivo":
        caminho = args["caminho"]
        aviso = f"\n[dim #00aaff]* Lendo arquivo '{caminho}'... *[/dim #00aaff]\n"
        resultado = ler_arquivo(caminho)

    elif nome == "escrever_arquivo":
        caminho = args["caminho"]
        conteudo = args["conteudo"]
        aviso = f"\n[dim #00aaff]* escrevendo arquivo '{caminho}'... *[/dim #00aaff]\n"
        resultado = escrever_arquivo(caminho, conteudo)

    else:
        return nome, None, None

    if inspect.isawaitable(resultado):
        resultado = await resultado

    return nome, resultado, aviso


async def falar(content: str):
    async with _memory_lock:
        agora_hora = datetime.now().strftime("%H:%M")
        agora_completo = datetime.now().strftime("%d/%m/%Y %H:%M")

        memory.append({
            "role": "user",
            "content": f"[{agora_hora}] {content}"
        })

        persona_ativa = memory_manager.current_persona.replace("amadeus_", "")

        try:
            facts, rag_data = await asyncio.gather(
                memory_manager.buscar_fatos_relevantes(content),
                rag_engine.consultar_data(content, persona=persona_ativa)
            )
        except Exception as e:
            print(">>> erro ao buscar fatos/RAG:", e)
            facts, rag_data = "", ""

        prompt_atual = memory_manager.vies[0]["content"]

        system_content = (
            f"{prompt_atual}\n\n"
            f"Pesquisa sobre o usuario:\n{facts}\n\n"
            f"Pesquisa no banco de dados (RAG):\n{rag_data}\n\n"
            f"Linha do tempo atual: {agora_completo} (Não cite isso do nada)."
        )

        iteracao = 0

        while True:
            messages = [
                {"role": "system", "content": system_content},
                *memory
            ]

            full_response = ""
            tool_calls = []

            try:
                async for tipo, data in stream_response(messages):
                    if tipo == "text":
                        full_response += data
                        yield data
                    else:
                        tool_calls = data["tool_calls"]
            except Exception as e:
                yield f"\n[bold red]* Erro ao falar com o modelo: {e} *[/bold red]\n"
                _trim_memory()
                memory_manager.save(memory)
                return

            if not tool_calls or iteracao >= MAX_TOOL_ITERATIONS:
                if not tool_calls or iteracao >= MAX_TOOL_ITERATIONS:
                    # Se veio vazio, força a síntese com UM ÚNICO CHAMADA EXTRA
                    if not full_response.strip():
                        # Pega os resultados das tools guardadas na memória
                        tool_results = [f"{m.get('name')}: {m.get('content')}" for m in memory if
                                        m.get('role') == 'tool']

                        if tool_results:
                            # Roda o modelo UMA vez só pra gerar o resumo (sem tools, sem loop)
                            final_stream = await AsyncClient().chat(
                                model=model,
                                messages=[
                                    {"role": "system",
                                     "content": f"{system_content}\n\nGere uma resposta final clara para o usuário com base APENAS nos resultados das ferramentas listados abaixo. Se não tiver dados, diga que não encontrou."},
                                    *memory,
                                    {"role": "user", "content": f"Resultados obtidos:\n{chr(10).join(tool_results)}"}
                                ],
                                stream=True
                            )
                            # Renderiza essa resposta final pro usuário
                            async for chunk in final_stream:
                                if chunk.message.content:
                                    yield chunk.message.content
                                    full_response += chunk.message.content
                        else:
                            full_response = "Não consegui executar nenhuma ferramenta para responder."

                    # Agora sim guarda e sai
                    memory.append({"role": "assistant", "content": full_response})
                    break

            # Salva a resposta parcial + as tool calls pedidas
            memory.append({
                "role": "assistant",
                "content": full_response,
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": t.function.name,
                            "arguments": t.function.arguments
                        }
                    }
                    for t in tool_calls
                ]
            })

            # EXECUTA TOOLS
            for tool in tool_calls:
                nome, resultado, aviso = await _executar_tool(tool)

                if nome is None:
                    continue

                if aviso:
                    yield aviso

                memory.append({
                    "role": "tool",
                    "name": nome,
                    "content": resultado
                })

            iteracao += 1
            # volta pro topo do loop e gera de novo com os resultados das tools

        _trim_memory()
        memory_manager.save(memory)