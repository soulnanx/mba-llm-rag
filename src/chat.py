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

    while True:
        user_input = input("Digite sua mensagem: ")
        if user_input.strip().lower() in ["sair", "exit", "quit"]:
            print("Encerrando a conversa. Até logo!")
            break
        
        try:
            # Construir a cadeia sem a LLM no final
            chain = rag_result | setup_rag_chain
            
            # Executar a cadeia (sem a LLM)
            result = chain.invoke({"user_question": user_input})
            
            # Enviar o prompt formatado para a LLM
            response_content = llm.invoke(result["prompt"])
            print(f"\n🤖 Resposta: {response_content.content}")

        except Exception as e:
            print(f"Erro ao processar mensagem: {str(e)}")
            print("-" * 30)

if __name__ == "__main__":
    validate_env()
    main()