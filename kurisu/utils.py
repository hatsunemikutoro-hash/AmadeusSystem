import os.path

from ollama import AsyncClient
from pynput import keyboard

model = "qwen3.5:9b"
from kurisu.brain_func.state import state
import re
import trafilatura
from ddgs import DDGS

LOCK_SEARCH = False
FILE_WRITE = False

PROJETO_RAIZ = "S:\\Vscode\\MakiseAI"

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
    },
{
        "type": "function",
        "function": {
            "name": "listar_diretorio",
            "description": "Lista os arquivos e pastas de um diretório. Use para navegar pelo projeto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho": {"type": "string", "description": "Caminho para listar. Use '.' para atual, '..' para subir."}
                },
                "required": ["caminho"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ler_arquivo",
            "description": "Lê o conteúdo de um arquivo de texto (código, logs, etc). Útil para debugar ou entender o código.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho": {"type": "string", "description": "Caminho do arquivo para ler"}
                },
                "required": ["caminho"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escrever_arquivo",
            "description": "CRIA ou SOBRESCREVE um arquivo com novo conteúdo com seu formato desejado. Use para corrigir bugs, refatorar ou criar novos arquivos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho": {"type": "string", "description": "Caminho do arquivo para escrever"},
                    "conteudo": {"type": "string", "description": "Conteúdo NOVO para colocar no arquivo"}
                },
                "required": ["caminho", "conteudo"]
            }
        }
    }
]

def search(termo: str) -> str:
    if not LOCK_SEARCH:
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
            return f"erro ao acessar a api de search. ERRO {e}"
    else:
        return f"O LOCK_SEARCH foi ativado pelo usuario, o conteudo dessa conversa provavelmente é secreto."

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

# spcprrp

def _sanitizar_caminho(caminho):
    global PROJETO_RAIZ
    if not caminho:
        return PROJETO_RAIZ

    if caminho.startswith("."):
        caminho = os.path.join(PROJETO_RAIZ, caminho)

    caminho_abs = os.path.abspath(caminho)

    if not caminho_abs.startswith(os.path.abspath(PROJETO_RAIZ)):
        return PROJETO_RAIZ

    return caminho_abs

def listar_diretorio(caminho="."):
    caminho_real = _sanitizar_caminho(caminho)

    if not os.path.exists(caminho_real):
        return f"Erro: Caminho {caminho_real} não encontrado."

    try:
        itens = os.listdir(caminho_real)
        resultado = f"Conteudo de {caminho_real}:\n"
        for item in sorted(itens):
            caminho_completo = os.path.join(caminho_real, item)
            if os.path.isdir(caminho_completo):
                resultado += f"  📂 {item}/\n"
            else:
                tamanho = os.path.getsize(caminho_completo)
                resultado += f"  📄 {item} ({tamanho} bytes)\n"
        return resultado
    except Exception as e:
        return f"Erro ao listar: {e}"

def ler_arquivo(caminho):
    global PROJETO_RAIZ
    raiz = PROJETO_RAIZ
    if not os.path.isabs(caminho):
        caminho = os.path.join(raiz, caminho)

    caminho = os.path.normpath(caminho)
    if not caminho.startswith(raiz):
        return f"SISTEMA AMADEUS AVISO: {caminho} ESTÁ FORA DO PROJETO"

    if not os.path.exists(caminho):
        return f"SISTEMA AMADEUS AVISO: {caminho} NAO EXISTE"

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        try:
            with open(caminho, 'r', encoding='latin-1') as f:
                conteudo = f.read()
        except Exception as e:
            return f"❌ Não foi possível decodificar o arquivo: {e}"

    limite = 10000

    if len(conteudo) > limite:
        conteudo = conteudo[:limite] + "\n\n... [ARQUIVO MUITO GRANDE - CORTADO] ..."

    return f"📄 Conteúdo de '{caminho}':\n```\n{conteudo}\n```"

def escrever_arquivo(caminho: str, conteudo: str):
    caminho_real = _sanitizar_caminho(caminho)
    if FILE_WRITE:
        with open(caminho_real, 'w', encoding="utf-8") as file:
            file.write(conteudo)
    else:
        return f"O usuario ativou a trava de segurança FILE_WRITE que não permite a modificação de arquivos."
