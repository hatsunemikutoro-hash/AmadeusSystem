import asyncio
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_DIR = "S:/Vscode/MakiseAI/kurisu/memory/amadeus_cortex"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_dbs = {
    "kurisu": Chroma(collection_name="amadeus_kurisu", embedding_function=embeddings, persist_directory=DB_DIR),
    "valkyrie": Chroma(collection_name="amadeus_valkyrie", embedding_function=embeddings, persist_directory=DB_DIR),
    "skuld": Chroma(collection_name="amadeus_skuld", embedding_function=embeddings, persist_directory=DB_DIR),
    "gold": Chroma(collection_name="amadeus_kurisu", embedding_function=embeddings, persist_directory=DB_DIR)
}

async def consultar_data(pergunta, persona="kurisu"):
    db_ativo = vector_dbs.get(persona, vector_dbs["kurisu"])

    resultados = await asyncio.to_thread(
        db_ativo.similarity_search_with_score,
        pergunta,
        k=3
    )

    if not resultados:
        return "Nenhum dado encontrado."

    doc, score = resultados[0]

    print(f"DEBUG [{persona.upper()}]: Pergunta: '{pergunta}' | Melhor Score: {score}")

    if score < 1.0:
        return doc.page_content
    else:
        return f"Não encontrei nada com relevância suficiente (Score: {score})"


async def salvar_no_cerebro(texto, persona="kurisu"):
    db_ativo = vector_dbs.get(persona, vector_dbs["kurisu"])
    
    await asyncio.to_thread(db_ativo.add_texts, [texto])
    print(f">>> Amadeus [{persona.upper()}]: Informação inserida com sucesso no data base")


def limpar_mente_da_persona(persona):
    if persona in vector_dbs:
        try:
            vector_dbs[persona].delete_collection()
            print(f"Memórias da persona [{persona.upper()}] wipadas")
            
            # Reinicializa a instância limpa para evitar referências nulas
            vector_dbs[persona] = Chroma(collection_name=f"amadeus_{persona}", embedding_function=embeddings, persist_directory=DB_DIR)
        except Exception as e:
            print(f" Erro ao tentar wipar o db da {persona}: {str(e)}")
    else:
        print(f"Persona '{persona}' não identificada no banco de dados.")
        
        
if __name__ == "__main__":

    async def iniciar_experimento():

        await salvar_no_cerebro(
            texto="""""",
            persona="skuld"
        )


        print("\n [SUCESSO]: Dados iniciais cravados no banco de dados!")
        

    asyncio.run(iniciar_experimento())
