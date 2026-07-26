from ollama import AsyncClient
from pynput import keyboard

model = "qwen3.5:9b"
from kurisu.brain_func.state import state
import re
import trafilatura
from ddgs import DDGS

ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": (
                "Busca informações em tempo real na internet. "
                "Use sempre que o usuário perguntar sobre eventos atuais, "
                "notícias, documentações recentes ou fatos desconhecidos."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "termo": {
                        "type": "string",
                        "description": "O termo ou frase curta para pesquisar."
                    }
                },
                "required": ["termo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": (
                "Realiza uma análise interna profunda antes da resposta final. "
                "Use SOMENTE quando a tarefa exigir raciocínio complexo, "
                "planejamento, arquitetura de software, engenharia, matemática, "
                "depuração difícil, resolução de problemas em múltiplas etapas ou "
                "quando houver incerteza sobre a melhor resposta. "
                "Não utilize para perguntas simples, conversas casuais, traduções, "
                "cumprimentos ou tarefas diretas."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A mensagem completa do usuário que deve ser analisada."
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]

def search(termo: str) -> str:
    try:


        results = DDGS().text(termo, max_results=1)

        url = results[0]['href']

        conteudo = trafilatura.fetch_url(url)
        limpin = trafilatura.extract(conteudo,
                                     output_format='markdown',
                                     include_tables=True,
                                     include_comments=False,
                                     favor_recall=True)

        return limpin
    except Exception as e:
        return f"erro ao acessar o steins gate. ERRO {e}"

async def think(objetivo: str):
    prompt = f"""
Você é um mecanismo interno de planejamento.

Sua tarefa NÃO é responder ao usuário.

Analise profundamente o problema abaixo.

- Quebre em etapas.
- Procure inconsistências.
- Considere alternativas.
- Pense como um engenheiro.
- Crie um plano de execução.

Retorne SOMENTE o plano.
Não converse com o usuário.

Problema:
{objetivo}
"""

    response = await AsyncClient().chat(
        model=model,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )

    return response.message.content

def on_press(key):
    if state.mode == "v":
        try:
            if key == keyboard.Key.space:
                listening = not state.listening
                print(f"Kurisu {'Activate' if listening else 'Sleeping'}")
        except Exception as e:
            print(f"Erro tecla: {e}")

