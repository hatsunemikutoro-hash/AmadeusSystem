from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DB_DIR = "S:/Vscode/MakiseAI/kurisu/memory/amadeus_cortex"

# Crie um arquivo temporário: indexar_projeto.py
import asyncio
from kurisu.memory.rag_engine import salvar_no_cerebro
import os

# wipe_valkyrie.py
import os
import shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSONA = "valkyrie"


def wipe_valkyrie():
    """Remove APENAS a coleção da Valkyrie"""

    print(f"🧹 Limpando memórias da {PERSONA.upper()}...")

    try:
        # 1. Tenta deletar via Chroma
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        db = Chroma(
            collection_name=f"amadeus_{PERSONA}",
            embedding_function=embeddings,
            persist_directory=DB_DIR
        )

        # Deleta a coleção
        db.delete_collection()
        print(f"✅ Coleção 'amadeus_{PERSONA}' deletada via Chroma")

    except Exception as e:
        print(f"⚠️ Erro ao deletar via Chroma: {e}")
        print("📁 Tentando remoção manual...")

        # 2. Fallback: deletar a pasta manualmente
        caminho_colecao = os.path.join(DB_DIR, f"amadeus_{PERSONA}")

        if os.path.exists(caminho_colecao):
            shutil.rmtree(caminho_colecao)
            print(f"✅ Pasta '{caminho_colecao}' removida manualmente")
        else:
            print(f"❌ Pasta não encontrada: {caminho_colecao}")

    # 3. (OPCIONAL) Listar o que sobrou
    print("\n📂 Coleções restantes:")
    for pasta in os.listdir(DB_DIR):
        if os.path.isdir(os.path.join(DB_DIR, pasta)):
            print(f"  • {pasta}")


# if __name__ == "__main__":
#     # CONFIRMAÇÃO ANTES DE APAGAR
#     print("⚠️ ATENÇÃO: Isso vai apagar TODAS as memórias da VALKYRIE!")
#     resposta = input("Digite 'SIM' para confirmar: ")
#
#     if resposta.upper() == "SIM":
#         wipe_valkyrie()
#         print("\n✅ Valkyrie resetada com sucesso!")
#     else:
#         print("❌ Operação cancelada.")


# Versão de teste (indexa só 1 arquivo)
async def testar_um_arquivo():
    from kurisu.memory.rag_engine import salvar_no_cerebro

    path = "S:\\Vscode\\MakiseAI\\kurisu\\utils.py"
    with open(path, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    await salvar_no_cerebro(
        f"ARQUIVO DO SISTEMA AMADEUS: utils.py\n\n{conteudo}",
        persona="valkyrie"
    )
    print("✅ Indexado!")





def aprender_livro(caminho_pdf, persona="kurisu"):
    """
    Carrega um PDF e o assimila na coleção correta da Amadeus.
    Se as pastas ou coleções não existirem, o Chroma as criará automaticamente
    """
    nome_da_colecao = f"amadeus_{persona}"

    print(f"[{persona.upper()}] Iniciando leitura do arquivo de dados: {caminho_pdf}...")

    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
        collection_name=nome_da_colecao
    )

    print(f"Sucess [{persona.upper()}].")


aprender_livro("S:\\Vscode\\MakiseAI\\kurisu\\memory\\books\\Valkyrie\\C Completo e Total (Schildit 3ªed.).pdf", persona="valkyrie")

