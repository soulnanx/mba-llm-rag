import os
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.runnables import chain
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = """
CONTEXTO:
{rag_data}

REGRAS:
- Responda SOMENTE com base no CONTEXTO fornecido.
- NUNCA faça inferências, deduções ou interpretações.
- NUNCA conte ou calcule quantidades baseado em padrões visuais.
- NUNCA assuma que dados em uma lista representam "clientes" ou "quantidades".
- Se a informação não estiver EXPLICITAMENTE declarada no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

<important>O QUE NÃO FAZER:</important>
- NÃO conte itens em listas
- NÃO calcule totais ou médias
- NÃO assuma que empresas listadas são "clientes"
- NÃO faça inferências sobre relacionamentos entre dados
- NÃO interprete anos como "quantidade de clientes"

<important>EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:</important>

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."
Explicação: A lista de empresas não especifica quantos são "clientes" nem fornece contagem.

Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Conte quantas empresas têm no nome 'Vanguarda'"
Resposta: "Não tenho informações necessárias para responder sua pergunta."
Explicação: Não posso contar ou fazer cálculos baseado no texto fornecido.

INSTRUÇÃO FINAL:
Analise APENAS o que está EXPLICITAMENTE declarado no CONTEXTO.
Se a pergunta requerer contagem, cálculo, inferência ou interpretação
que não esteja claramente expressa no texto, responda:
"Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{user_question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

@chain
def setup_rag_chain(rag_dict: dict) -> dict:
    prompt = PromptTemplate(
        input_variables=["rag_data", "user_question"],
        template=PROMPT_TEMPLATE)

    # Formatar o prompt com os dados reais
    formatted_prompt = prompt.format(
        rag_data=rag_dict.get("rag_data", ""),
        user_question=rag_dict.get("user_question", "")
    )
    
    # Debug técnico - exibir o prompt completo que será enviado para o modelo
    print(f"[RAG] Prompt formatado - {len(formatted_prompt)} chars")
    print(f"[RAG] Dados processados: {len(rag_dict.get('rag_data', ''))} chars")
    print(f"[RAG] Variáveis encontradas: {list(rag_dict.keys())}")
    print(f"\n{'='*80}")
    print("PROMPT COMPLETO QUE SERÁ ENVIADO PARA O MODELO:")
    print(f"{'='*80}")
    print(formatted_prompt)
    print(f"{'='*80}")
    
    return {
        "prompt": formatted_prompt,
        "rag_data": rag_dict.get("rag_data"),
        "user_question": rag_dict.get("user_question")
    }

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
