import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search import setup_rag_chain, rag_result

load_dotenv()

def validate_env():
    for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

llm = ChatOpenAI(model="gpt-5-mini", disable_streaming=True, temperature=0)

def main():
    user_input = input("Digite sua mensagem: ")

    chain = rag_result | setup_rag_chain | llm
    response_content = chain.invoke({"user_question": user_input}) 

    print("LLM: " + response_content.content)

if __name__ == "__main__":
    validate_env()
    main()