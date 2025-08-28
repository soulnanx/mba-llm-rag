import os
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.runnables import chain
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = """
Voce é um especialista em respoder sobre {mastery} baseado no contexto abaixo

CONTEXTO: {rag_data}

IMPORTANTE:
- voce nao fala que sabe sobre o contexto, voce responde somente a pergunta do usuario com os dados do contexto que foi passado
- se a informação nao tem no contexto informado, RESPONDA SOMENTE: "Não tenho informações necessárias para responder sua pergunta." e nenhuma informação adicional

RESPONDA A PERGUNTA DO USUÁRIO: {user_question}
"""

@chain
def setup_rag_chain(rag_dict: dict) -> dict:
    return PromptTemplate(
        input_variables=["rag_data", "user_question", "mastery"],
        template=PROMPT_TEMPLATE)

@chain
def rag_result(user_input_dict: dict) -> dict:
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )

    results = store.similarity_search_with_score(user_input_dict["user_question"], k=10)

    formatted_output = ""
    mastery = ""
    for i, (doc, score) in enumerate(results, start=1):
        formatted_output += "="*50 + "\n"
        formatted_output += f"Resultado {i} (score: {score:.2f}):\n"
        formatted_output += "="*50 + "\n\n"
        formatted_output += "Texto:\n"
        formatted_output += doc.page_content.strip() + "\n\n"
        mastery = doc.metadata["mastery"]

    user_input_dict["rag_data"] = formatted_output
    user_input_dict["mastery"] = mastery
 
    return user_input_dict
