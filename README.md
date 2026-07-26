# SISTEMA AMADEUS

Projeto focado na execução de **Inteligência Artificial local**, priorizando **privacidade, controle e autonomia**.
O objetivo é fornecer um ambiente funcional e personalizado, executando diretamente no seu computador sem depender de serviços externos.

---

## 🛠 Funcionalidades

### Interface no Terminal

Interface desenvolvida com **Textual**, permitindo interação com a IA diretamente pelo console de forma organizada e intuitiva.

### RAG com ChromaDB

Sistema de **Retrieval-Augmented Generation (RAG)** para busca inteligente em documentos.

O projeto já inclui alguns livros pré-carregados para testes e demonstração da capacidade de consulta contextual.

### Deep Think

Ferramentas voltadas para aprimoramento de raciocínio e processamento de informações.

> Status: em manutenção, porém com funcionalidades disponíveis.

### Search Tools

Ferramentas de busca na web para ampliar o conhecimento da IA através de informações externas.

> Requer conexão com a internet para funcionamento.

---

# Como utilizar

## 1. Instale as dependências

Execute:

```bash
pip install -r requirements.txt
```

---

## 2. Prepare o Ollama

Certifique-se de que o **Ollama** esteja instalado e em execução.

Escolha o modelo de IA que deseja utilizar e faça o download conforme sua preferência.

---

## 3. Configure o modelo

O modelo padrão atual é:

```text
qwen3.5:9b
```

Para alterar:

1. Abra o arquivo:

```text
kurisu/brain_func/core.py
```

2. Localize a variável responsável pelo modelo.

3. Substitua pelo modelo desejado.

---

## 4. Inicie o projeto

Execute:

```bash
python textual_test.py
```

---

## Privacidade em primeiro lugar

O **AMADEUS KURISU** foi desenvolvido com foco em uma experiência de IA local, oferecendo maior controle sobre dados, modelos e ambiente de execução.

**El Psy Kongroo.**
