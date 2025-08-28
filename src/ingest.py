import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv()

# validacao variaveis
for k in ("OPENAI_API_KEY", "PGVECTOR_URL","PGVECTOR_COLLECTION"):
    if not os.getenv(k):
        raise RuntimeError(f"Environment variable {k} is not set")

def process_pdfs_by_chunks(pdf_dir):
    """Processa PDFs quebrando por chunks"""
    pdf_files = list(pdf_dir.glob("*.pdf"))
    all_docs = []
    
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs_from_pdf = loader.load()
        file_name_without_extension = pdf_file.stem
        for doc in docs_from_pdf:
            doc.metadata["mastery"] = file_name_without_extension
        all_docs.extend(docs_from_pdf)
    
    # Quebra por chunks
    if all_docs:
        splits = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150, 
            add_start_index=False
        ).split_documents(all_docs)
        
        # Adiciona metadados de chunk aos documentos
        for i, split in enumerate(splits):
            split.metadata["chunk_id"] = i
            split.metadata["processing_type"] = "chunk"
        
        return splits
    return []

def process_pdfs_by_pages(pdf_dir):
    """Processa PDFs mantendo por páginas"""
    pdf_files = list(pdf_dir.glob("*.pdf"))
    all_docs = []
    
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs_from_pdf = loader.load()
        file_name_without_extension = pdf_file.stem
        for doc in docs_from_pdf:
            doc.metadata["mastery"] = file_name_without_extension
            doc.metadata["processing_type"] = "page"
        all_docs.extend(docs_from_pdf)
    
    return all_docs

# busca dos pdfs das duas subpastas
current_dir = Path(__file__).parent
pdf_base_dir = current_dir / "pdf"

# Verifica se as subpastas existem
chunk_dir = pdf_base_dir / "chunk"
page_dir = pdf_base_dir / "page"

if not chunk_dir.exists():
    print(f"Aviso: Pasta 'chunk' não encontrada em {pdf_base_dir}")
if not page_dir.exists():
    print(f"Aviso: Pasta 'page' não encontrada em {pdf_base_dir}")

# Processa PDFs por chunks
chunk_docs = []
if chunk_dir.exists():
    chunk_docs = process_pdfs_by_chunks(chunk_dir)
    print(f"Processados {len(chunk_docs)} chunks de PDFs da pasta 'chunk'")

# Processa PDFs por páginas
page_docs = []
if page_dir.exists():
    page_docs = process_pdfs_by_pages(page_dir)
    print(f"Processadas {len(page_docs)} páginas de PDFs da pasta 'page'")

# Combina todos os documentos
all_docs = chunk_docs + page_docs

if not all_docs:
    print("Nenhum PDF encontrado para processar")
    raise SystemExit(0)

# enriquecimento de dados
enriched = [
    Document(
        page_content=d.page_content,
        metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
    )
    for d in all_docs
]    

ids = [f"doc-{i}" for i in range(len(enriched))]

embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))

store = PGVector(
    embeddings=embeddings,
    collection_name=os.getenv("PGVECTOR_COLLECTION"),
    connection=os.getenv("PGVECTOR_URL"),
    use_jsonb=True,
)

store.add_documents(documents=enriched, ids=ids)

print(f"Total de {len(enriched)} documentos processados e adicionados ao banco de dados")
