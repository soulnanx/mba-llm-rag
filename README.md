# Desafio MBA Engenharia de Software com IA - Full Cycle

Este projeto implementa um sistema de busca semântica com RAG (Retrieval-Augmented Generation) utilizando PostgreSQL com extensão pgvector.

## 🚀 **FACILITE SEU DESENVOLVIMENTO COM O MAKEFILE!**

**Temos um Makefile completo que facilita todas as operações!** Use `make help` para ver todos os comandos disponíveis.

```bash
# Ver todos os comandos disponíveis
make help

# Executar ingestão de documentos
make ingest

# Executar chat interativo
make run

# Testar perguntas específicas
make test-inferencia      # Testa pergunta que requer inferência
make test-explicita       # Testa pergunta com informação explícita
```

## Pré-requisitos

- **Docker e Docker Compose**: Certifique-se de ter o Docker e Docker Compose instalados em sua máquina
  - [Instalar Docker](https://docs.docker.com/get-docker/)
  - [Instalar Docker Compose](https://docs.docker.com/compose/install/)

- **Python 3.8+**: Certifique-se de ter Python 3.8 ou superior instalado

## Como executar a solução

### 1. Configurar o ambiente de banco de dados

Primeiro, inicie os serviços do banco de dados PostgreSQL com pgvector:

```bash
docker compose up -d
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

#### **Opção 1: Usando o Makefile (RECOMENDADO)**
```bash
# Ingerir documentos
make ingest

# Executar chat interativo
make run

# Testar funcionalidades específicas
make test-inferencia      # Testa pergunta que requer inferência
make test-explicita       # Testa pergunta com informação explícita
```

#### **Opção 2: Execução manual**
```bash
# Subir o banco de dados:
docker compose up -d

# Executar ingestão do PDF:
python src/ingest.py

# Rodar o chat:
python src/chat.py
```

## 🎯 **Melhorias Implementadas no Sistema RAG**

### **Prompt Robusto e Consistente**
O sistema agora possui um prompt extremamente robusto que previne interpretações incorretas:

- **✅ Regras Claras**: Instruções específicas sobre o que NÃO fazer
- **✅ Exemplos Concretos**: Casos de uso com explicações detalhadas
- **✅ Consistência Total**: Respostas consistentes para perguntas similares
- **✅ Prevenção de Inferências**: Evita interpretações incorretas de dados estruturados

### **Comportamento Validado**
- **Perguntas que requerem inferência**: Responde consistentemente "Não tenho informações necessárias"
- **Perguntas com informações explícitas**: Extrai e responde corretamente
- **Debug completo**: Logs detalhados para facilitar desenvolvimento e troubleshooting

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

- `src/` - Código fonte da aplicação
  - `ingest.py` - Script de ingestão de documentos
  - `search.py` - Sistema de busca semântica com prompt robusto
  - `chat.py` - Interface de chat com RAG
- `src/pdf/` - Documentos para processamento
  - `chunk/` - PDFs para processamento por chunks
  - `page/` - PDFs para processamento por páginas
- `docker-compose.yml` - Configuração dos serviços Docker
- `requirements.txt` - Dependências Python
- `Makefile` - **Comandos automatizados para facilitar o desenvolvimento**
- `document.pdf` - Documento de exemplo para ingestão

## Parando os serviços

Para parar os serviços Docker:

```bash
docker compose down
```

Para remover também os volumes de dados:

```bash
docker compose down -v
```

## 🚀 **Uso Rápido - Comandos Essenciais**

```bash
# 1. Iniciar o banco de dados
docker compose up -d

# 2. Configurar ambiente Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Executar com Makefile (RECOMENDADO)
make help                    # Ver todos os comandos
make ingest                  # Ingerir documentos
make run                     # Chat interativo
make test-inferencia        # Testar pergunta que requer inferência
make test-explicita         # Testar pergunta com informação explícita

# 4. Parar serviços
docker compose down
```

## 📚 **Exemplos de Uso**

### **Teste de Consistência**
```bash
# Execute 3 vezes para validar consistência
make test-inferencia
make test-inferencia
make test-inferencia
```

### **Teste de Extração de Informações**
```bash
# Testar extração de informações explícitas
make test-explicita
```

**O Makefile torna o desenvolvimento muito mais eficiente e profissional!** 🎯