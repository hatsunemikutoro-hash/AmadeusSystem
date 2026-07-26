import json
import os
import aiofiles

# Amadeus Kurisu // Amadeus Valkyrie // Amadeus Skuld
caminho_memories = os.path.dirname(os.path.abspath(__file__))

vies = [{"role": "system", "content": ""}]
current_persona = "amadeus_kurisu"
character_prompt = "prompt_initial_kurisu"

# esquizofrenia system
def mudar_persona(nome_persona):
    """Muda a persona ativa e recarrega dinamicamente o arquivo TXT correspondente"""
    global current_persona
    global  character_prompt
    
    if nome_persona in ["kurisu", "amadeus_kurisu"]:
        character_prompt = "prompt_initial_kurisu"
        current_persona = "amadeus_kurisu"
    elif nome_persona in ["valkyrie", "amadeus_valkyrie"]:
        character_prompt = "prompt_initial_valkyrie"
        current_persona = "amadeus_valkyrie"
    elif nome_persona in ["gold", "amadeus_gold"]:
        character_prompt = "prompt_initial_gold"
        current_persona = "amadeus_gold"
    elif nome_persona in ["skuld", "amadeus_skuld"]:
        character_prompt = "prompt_initial_skuld"
        current_persona = "amadeus_skuld"
    else:
        character_prompt = "prompt_initial_kurisu"
        current_persona = "amadeus_kurisu"

    caminho_file = os.path.join(caminho_memories, character_prompt)
    
    try:
        with open(caminho_file, 'r', encoding='utf-8') as file:
            prompt_conteudo = file.read()
            vies[0]["content"] = prompt_conteudo
        print(f"Prompt carregado de: {character_prompt}")
    except FileNotFoundError:
        print(f"Arquivo de prompt '{character_prompt}' não foi encontrado em {caminho_memories}")
        vies[0]["content"] = f"O sistema deu erro por favor avise ao usuario que o sistema deu erro."


def save_facts(new_facts):
    caminho = os.path.join(caminho_memories, "facts.json")

    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            existing_facts = json.load(f)
    else:
        existing_facts = []

    allFacts = list(set(existing_facts + new_facts))

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(allFacts, f, ensure_ascii=False, indent=2)

def load_facts():
    caminho = os.path.join(caminho_memories, "facts.json")

    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


async def buscar_fatos_relevantes(pergunta):
    caminho = os.path.join(caminho_memories, "facts.json")
    async with aiofiles.open(caminho, mode='r', encoding='utf-8') as f:
        conteudo = await f.read()
        fatos = json.loads(conteudo)

    palavras_pergunta = pergunta.lower().split()
    relevantes = [
        f for f in fatos
        if any(palavra in f.lower() for palavra in palavras_pergunta)
    ]

    return relevantes

def load_memory():
    if os.path.exists(os.path.join(caminho_memories, "memories.json")):
        with open(os.path.join(caminho_memories, "memories.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [m for m in data if m["role"] != "system"]
    else:
        with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
            return []

def save(data):
    with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def wipe():
    with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)

