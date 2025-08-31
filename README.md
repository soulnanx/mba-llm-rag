# Desafio MBA Engenharia de Software com IA - Full Cycle

Este projeto implementa um sistema de busca semântica com RAG (Retrieval-Augmented Generation) utilizando PostgreSQL com extensão pgvector, com arquitetura modular e bem estruturada.

## Pré-requisitos

- **Docker e Docker Compose**: Certifique-se de ter o Docker e Docker Compose instalados em sua máquina
  - [Instalar Docker](https://docs.docker.com/get-docker/)
  - [Instalar Docker Compose](https://docs.docker.com/compose/install/)

- **Python 3.8+**: Certifique-se de ter Python 3.8 ou superior instalado

## Como executar a solução

### 1. Configurar o ambiente de banco de dados

Primeiro, inicie os serviços do banco de dados PostgreSQL com pgvector:

```bash
docker-compose up -d
```

Este comando irá:
- Iniciar um container PostgreSQL com extensão pgvector
- Configurar o banco de dados `rag` com usuário `postgres`
- Expor a porta 5432 para conexões locais

### 2. Configurar o ambiente Python

Crie e ative um ambiente virtual Python:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação

Após configurar o banco de dados e instalar as dependências, você pode executar os scripts do projeto:

- `src/ingest.py` - Para ingerir documentos
- `src/chat.py` - Para interface de chat

## Arquitetura do Sistema

### Visão Geral

O sistema foi refatorado para seguir princípios de **Separação de Responsabilidades** e **Modularidade**, resultando em uma arquitetura mais limpa e manutenível.

### Componentes Principais

#### 1. **RAGService** (`src/search.py`)
- **Responsabilidade**: Gerenciar todas as operações RAG (Retrieval-Augmented Generation)
- **Funcionalidades**:
  - Conexão com banco de dados vetorial
  - Processamento de embeddings
  - Execução de buscas semânticas
  - Formatação de resultados

#### 2. **ChatInterface** (`src/chat.py`)
- **Responsabilidade**: Interface de conversa e gerenciamento de sessões
- **Funcionalidades**:
  - Gerenciamento de histórico de conversas
  - Criação e configuração de agentes
  - Processamento de mensagens do usuário
  - Interface de linha de comando

#### 3. **Ferramentas Modulares** (`src/search.py`)
- **create_document_search_tool()**: Ferramenta para busca em documentos
- **create_general_conversation_tool()**: Ferramenta para conversa geral
- **Funções Chain RAG**:
  - `create_rag_prompt()`: Cria prompts para processamento RAG
  - `retrieve_similar_documents()`: Recupera documentos similares
  - `format_document_results()`: Formata resultados para apresentação

### Benefícios da Refatoração

1. **Separação de Responsabilidades**: Cada módulo tem uma responsabilidade específica
2. **Reutilização**: Ferramentas podem ser facilmente reutilizadas em outros contextos
3. **Testabilidade**: Cada componente pode ser testado independentemente
4. **Manutenibilidade**: Mudanças isoladas não afetam outros componentes
5. **Escalabilidade**: Fácil adição de novas funcionalidades

## Decisões de Arquitetura

### Estratégias de Processamento de Documentos

O projeto implementa duas estratégias diferentes para processamento de documentos PDF, permitindo flexibilidade na criação de embeddings:

#### 1. Processamento por Chunks (`src/pdf/chunk/`)
- **Objetivo**: Quebra documentos em pedaços menores para busca mais granular
- **Configuração**: 
  - Tamanho do chunk: 1000 caracteres
  - Overlap: 150 caracteres
  - Usa `RecursiveCharacterTextSplitter` do LangChain
- **Vantagens**:
  - Busca mais precisa e contextualizada
  - Melhor para documentos longos e complexos
  - Permite encontrar informações específicas dentro de seções
- **Casos de uso**: Documentos técnicos, manuais, relatórios extensos

#### 2. Processamento por Páginas (`src/pdf/page/`)
- **Objetivo**: Mantém a integridade da página como unidade de informação
- **Configuração**: Preserva cada página do PDF como um documento único
- **Vantagens**:
  - Mantém o contexto natural da página
  - Mais simples de implementar e entender
  - Melhor para documentos com estrutura bem definida por página
- **Casos de uso**: Receitas, catálogos, documentos com layout específico

### Metadados e Rastreabilidade

Cada documento processado inclui metadados importantes:
- `mastery`: Nome do arquivo PDF de origem
- `processing_type`: Tipo de processamento ("chunk" ou "page")
- `chunk_id`: Identificador único do chunk (apenas para processamento por chunks)
- `page`: Número da página (apenas para processamento por páginas)

### Banco de Dados Vectorial

- **Tecnologia**: PostgreSQL com extensão pgvector
- **Modelo de Embeddings**: OpenAI text-embedding-3-small (configurável)
- **Armazenamento**: JSONB para metadados flexíveis
- **Coleção**: Configurável via variável de ambiente `PGVECTOR_COLLECTION`

## Estrutura do Projeto

```
src/
├── ingest.py              # Script de ingestão de documentos
├── search.py              # Sistema de busca semântica e ferramentas RAG
├── chat.py                # Interface de chat com RAG
└── pdf/                   # Documentos para processamento
    ├── chunk/             # PDFs para processamento por chunks
    └── page/              # PDFs para processamento por páginas
```

### Detalhamento dos Módulos

#### `src/search.py`
- **RAGService**: Classe principal para operações RAG
- **Funções Factory**: Criação de ferramentas para o agente
- **Funções Chain**: Pipeline de processamento RAG
- **Funções Legadas**: Compatibilidade com código anterior

#### `src/chat.py`
- **ChatInterface**: Classe principal para interface de conversa
- **Gerenciamento de Sessões**: Histórico de conversas por sessão
- **Configuração de Agentes**: Setup automático de ferramentas e prompts
- **Interface CLI**: Loop principal de interação

## Variáveis de Ambiente

Configure as seguintes variáveis de ambiente:

```bash
OPENAI_API_KEY=your_openai_api_key
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=your_collection_name
OPENAI_MODEL=text-embedding-3-small  # opcional, padrão
```

## Funcionalidades do Chat

O sistema de chat suporta dois tipos de interação:

1. **Busca em Documentos**: Para perguntas sobre conteúdo específico dos documentos
2. **Conversa Geral**: Para perguntas gerais, saudações e contexto de conversa

### Exemplos de Uso

```bash
# Iniciar o chat
python src/chat.py

# Exemplos de perguntas:
# - "Quantas calorias tem o bolo de milho?"
# - "Qual o preço do Fiesta 2012?"
# - "Olá, como você está?"
# - "Qual foi minha primeira pergunta?"
```

## Parando os serviços

Para parar os serviços Docker:

```bash
docker-compose down
```

Para remover também os volumes de dados:

```bash
docker-compose down -v
```

## Fluxo de Prompts do Sistema

O sistema utiliza um fluxo simples e eficiente para processar as perguntas dos usuários:

### Diagrama do Fluxo

![Fluxo de Prompts](fluxo_simples_prompts.png)

### Resumo do Processo

1. **Entrada do Usuário**: Pergunta é enviada para o sistema
2. **Agent**: Analisa a pergunta e decide qual ferramenta usar
3. **Tool**: Executa a ferramenta apropriada:
   - `search_document`: Para perguntas sobre documentos
   - `general_conversation`: Para conversa geral
4. **Prompt**: Aplica o prompt específico da ferramenta
5. **LLM**: Processa a resposta usando GPT-5-mini
6. **Resposta**: Retorna a resposta formatada para o usuário

### Prompts Utilizados

#### Prompt do Agent (Decisão)
```
Você é um assistente útil que pode usar ferramentas para responder perguntas.

Você tem acesso a duas ferramentas:
1. search_document: Para perguntas sobre o documento, receitas, ingredientes, calorias, etc.
2. general_conversation: Para perguntas gerais, sobre a conversa, histórico, etc.

*IMPORTANTE* Quando voce for responder com uma ferramenta, responda somente o que foi pedido, nao adicione nenhuma informação extra

Use o histórico da conversa para entender o contexto e escolher a ferramenta apropriada.
Se a pergunta for sobre o documento ou conteúdo específico, use search_document.
Se for uma pergunta geral ou sobre a conversa, use general_conversation.
```

#### Prompt RAG (search_document)
```
Voce é um especialista em respoder sobre {mastery} baseado no contexto abaixo

CONTEXTO: {rag_data}

IMPORTANTE:
- voce nao fala que sabe sobre o contexto, voce responde somente a pergunta do usuario com os dados do contexto que foi passado
- se a informação nao tem no contexto informado, RESPONDA SOMENTE: "Não tenho informações necessárias para responder sua pergunta." e nenhuma informação adicional

RESPONDA A PERGUNTA DO USUÁRIO: {user_question}
```

#### Prompt Geral (general_conversation)
```
You are a helpful assistant. Answer questions based on general knowledge and conversation context.
```

### Exemplos de Uso

- **"Quantas calorias tem o bolo de milho?"**
  → Agent → search_document → Prompt RAG → Resposta baseada em documentos

- **"Olá, como você está?"**
  → Agent → general_conversation → Prompt Geral → Resposta de conversa

## Melhorias Implementadas

### Refatoração de Código
- ✅ Separação clara de responsabilidades
- ✅ Nomes de funções mais descritivos e consistentes
- ✅ Arquitetura modular e escalável
- ✅ Compatibilidade com código legado
- ✅ Documentação inline melhorada

### Qualidade do Código
- ✅ Classes bem estruturadas
- ✅ Métodos com responsabilidades específicas
- ✅ Tratamento de erros adequado
- ✅ Type hints e docstrings
- ✅ Padrões de nomenclatura consistentes