import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from search import create_document_search_tool, create_general_conversation_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.agents import AgentExecutor, create_openai_tools_agent

load_dotenv()

def validate_env():
    """Valida se as variáveis de ambiente necessárias estão configuradas"""
    for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
        if not os.getenv(k):
            raise RuntimeError(f"Environment variable {k} is not set")

class ChatInterface:
    """Interface de conversa com gerenciamento de sessões e ferramentas"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5-mini", disable_streaming=True, temperature=0)
        self.session_store: dict[str, InMemoryChatMessageHistory] = {}
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
        self.conversational_chain = self._create_conversational_chain()
        self.config = {"configurable": {"session_id": "demo-session"}}
    
    def _create_tools(self):
        """Cria as ferramentas necessárias para o agente"""
        search_tool = create_document_search_tool(self.llm)
        general_tool = create_general_conversation_tool(self.llm)
        return [search_tool, general_tool]
    
    def _create_agent(self):
        """Cria o agente com as ferramentas configuradas"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Você é um assistente útil que pode usar ferramentas para responder perguntas.

Você tem acesso a duas ferramentas:
1. search_document: Para perguntas sobre o documento, receitas, ingredientes, calorias, etc.
2. general_conversation: Para perguntas gerais, sobre a conversa, histórico, etc.


*IMPORTANTE* Quando voce for responder com uma ferramenta, responda somente o que foi pedido, nao adicione nenhuma informação extra

Use o histórico da conversa para entender o contexto e escolher a ferramenta apropriada.
Se a pergunta for sobre o documento ou conteúdo específico, use search_document.
Se for uma pergunta geral ou sobre a conversa, use general_conversation."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_question}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def _create_conversational_chain(self):
        """Cria a cadeia conversacional com histórico"""
        return RunnableWithMessageHistory(
            self.agent_executor,
            self.get_session_history,
            input_messages_key="user_question",
            history_messages_key="history",
        )
    
    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Obtém ou cria o histórico de uma sessão"""
        session = self.session_store.get(session_id)
        if session is None:
            self.session_store[session_id] = InMemoryChatMessageHistory()
            session = self.session_store[session_id]
        return session
    
    def process_message(self, user_input: str) -> str:
        """Processa uma mensagem do usuário e retorna a resposta"""
        response_content = self.conversational_chain.invoke(
            {"user_question": user_input}, 
            config=self.config
        )
        return response_content["output"]
    
    def run(self):
        """Executa o loop principal da interface de conversa"""
        print("Chat iniciado! Digite 'sair' para encerrar.")
        print("-" * 50)
        
        while True:
            user_input = input("Você: ")
            if user_input.strip().lower() in ["sair", "exit", "quit"]:
                print("Encerrando a conversa. Até logo!")
                break
            
            try:
                response = self.process_message(user_input)
                print("Assistant:", response)
                print("-" * 30)
            except Exception as e:
                print(f"Erro ao processar mensagem: {str(e)}")
                print("-" * 30)

def main():
    """Função principal que inicializa e executa o chat"""
    validate_env()
    chat_interface = ChatInterface()
    chat_interface.run()

if __name__ == "__main__":
    main()