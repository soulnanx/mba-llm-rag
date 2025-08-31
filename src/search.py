import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.runnables import chain
from langchain.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

PROMPT_TEMPLATE = """
Voce é um especialista em respoder sobre {mastery} baseado no contexto abaixo

CONTEXTO: {rag_data}

IMPORTANTE:
- voce nao fala que sabe sobre o contexto, voce responde somente a pergunta do usuario com os dados do contexto que foi passado
- se a informação nao tem no contexto informado, RESPONDA SOMENTE: "Não tenho informações necessárias para responder sua pergunta." e nenhuma informação adicional

RESPONDA A PERGUNTA DO USUÁRIO: {user_question}
"""

class RAGService:
    """Serviço para gerenciar operações RAG (Retrieval-Augmented Generation)"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL", "text-embedding-3-small"))
        self.store = PGVector(
            embeddings=self.embeddings,
            collection_name=os.getenv("PGVECTOR_COLLECTION"),
            connection=os.getenv("PGVECTOR_URL"),
            use_jsonb=True,
        )
    
    def query_documents(self, question: str) -> str:
        """Executa busca RAG e retorna resposta formatada"""
        try:
            # Usa as funções chain globais
            rag_chain = retrieve_similar_documents | format_document_results | create_rag_prompt | self.llm
            result = rag_chain.invoke({"user_question": question})
            return result.content
        except Exception as e:
            return f"Erro ao buscar no documento: {str(e)}"

def create_document_search_tool(llm: ChatOpenAI) -> tool:
    """Cria a ferramenta de busca de documentos"""
    rag_service = RAGService(llm)
    
    @tool
    def search_document(question: str) -> str:
        """
        Use essa ferramenta quando a pergunta for sobre os seguintes carros:
        - Honda fit 2008
        - Fiesta 2012
        - Duster 2019

        Use esta ferramenta quando a pergunta for sobre as seguintes receitas: 
        - Brigadeiro
        - Bolo de milho 
        - Beijinho
        """
        return rag_service.query_documents(question)
    
    return search_document

def create_general_conversation_tool(llm: ChatOpenAI) -> tool:
    """Cria a ferramenta para conversa geral"""
    
    @tool
    def general_conversation(question: str) -> str:
        """
        Use esta ferramenta para perguntas gerais, sobre a conversa, 
        histórico, ou qualquer assunto que não seja específico do documento.
        
        Exemplos de quando usar:
        - Perguntas sobre a conversa anterior
        - Perguntas sobre o assistente
        - Saudações e conversas casuais
        - Perguntas gerais de conhecimento
        - Perguntas sobre o histórico da conversa
        """
        # Prompt simples para conversa geral
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer questions based on general knowledge and conversation context."),
            ("human", "{question}")
        ])
        
        chain = prompt | llm
        result = chain.invoke({"question": question})
        return result.content
    
    return general_conversation

# Funções chain para RAG - nomes mais descritivos
@chain
def create_rag_prompt(rag_dict: dict) -> dict:
    """Cria o prompt template para processamento RAG"""
    return PromptTemplate(
        input_variables=["rag_data", "user_question", "mastery"],
        template=PROMPT_TEMPLATE)

@chain
def retrieve_similar_documents(user_input_dict: dict) -> dict:
    """Recupera documentos similares do banco de dados vetorial"""
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL", "text-embedding-3-small"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )

    results = store.similarity_search_with_score(user_input_dict["user_question"], k=10)
    user_input_dict["rag_results"] = results
    return user_input_dict

@chain
def format_document_results(user_input_dict: dict) -> dict:
    """Formata os resultados da busca para o prompt RAG"""
    results = user_input_dict.get("rag_results", [])
    formatted_output = ""
    mastery = ""
    for i, (doc, score) in enumerate(results, start=1):
        formatted_output += "="*50 + "\n"
        formatted_output += f"Resultado {i} (score: {score:.2f}):\n"
        formatted_output += "="*50 + "\n\n"
        formatted_output += "Texto:\n"
        formatted_output += doc.page_content.strip() + "\n\n"
        mastery = doc.metadata.get("mastery", "")

    user_input_dict["rag_data"] = formatted_output
    user_input_dict["mastery"] = mastery
    # Remover os resultados brutos para não poluir o dicionário
    user_input_dict.pop("rag_results", None)
    return user_input_dict

# Funções legadas para compatibilidade (deprecated)
@chain
def setup_rag_chain(rag_dict: dict) -> dict:
    """DEPRECATED: Use create_rag_prompt instead"""
    return create_rag_prompt(rag_dict)

@chain
def rag_search(user_input_dict: dict) -> dict:
    """DEPRECATED: Use retrieve_similar_documents instead"""
    return retrieve_similar_documents(user_input_dict)

@chain
def rag_format(user_input_dict: dict) -> dict:
    """DEPRECATED: Use format_document_results instead"""
    return format_document_results(user_input_dict)
