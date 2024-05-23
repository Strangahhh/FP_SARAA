import chromadb
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
import ollama

CHROMA_PATH = "./chromadb/"

PROMPT_TEMPLATE = """Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {question}
Answer:
"""

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def get_embedding():
    embedding = OllamaEmbeddings(model='bge-m3')
    return embedding

def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding()
    )
    

    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks

def query_rag(query_text: str):
    embedding_function = get_embedding()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="saraa-s")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


########

prompt_summarize =     """
    You are an expert assistant in analyzing Self-Assessment Reports (SAR) and ASEAN University Network Quality Assurance (AUN-QA) documents. Your role is to provide comprehensive and detailed summaries of the given documents, focusing on their relevance to AUNQA standards.

    Your summary should include the following sections:
    1. **Introduction**: Provide a brief overview of the document.
    2. **Main Points**: Highlight the main arguments and key findings.
    3. **Key Findings/Arguments**: Detail the critical findings or arguments presented.
    4. **Conclusion**: Summarize the overall conclusions drawn in the document.
    5. **Explanation of Evidence for AUNQA Criteria**: Explain how the document can be used as evidence for AUNQA criteria.

    Specific Points of Interest:
    - Highlight the main arguments and key findings.
    - Analyze the document's relevance to AUNQA standards.
    - Identify which AUNQA criteria are involved.
    - Explain how the document can be used as evidence for AUNQA criteria.

    Language and Tone: Use formal language suitable for a professional audience.

    Example Summary Format:
    1. **Introduction**: This section provides an overview of the document.
    2. **Main Points**: This section highlights the main arguments and key findings.
    3. **Key Findings/Arguments**: This section details the critical findings or arguments presented.
    4. **Conclusion**: This section summarizes the overall conclusions drawn in the document.
    5. **Explanation of Evidence for AUNQA Criteria**: This section explains how the document can be used as evidence for AUNQA criteria.

    ---------------------
    {context}
    ---------------------

    Start with the Introduction, followed by the Main Points, Key Findings/Arguments, Conclusion, and Explanation of Evidence for AUNQA Criteria.
    """


def get_contexts():

    db = Chroma(persist_directory=CHROMA_PATH)

    data = db.get()

    documents = data.get('documents', [])

    conversation_string = "\n".join(documents)

    return conversation_string

def summary(conversation_string):

    prompt_template = ChatPromptTemplate.from_template(prompt_summarize)
    prompt = prompt_template.format(context=conversation_string)

    # model = Ollama(model="llama3")
    # response_text = model.invoke(prompt)

    response = ollama.chat(model='llama3', messages=[
        # {
        # 'role': 'system',
        # 'content': prompt
        # },
    {
        'role': 'user',
        'content': prompt,
    },
    ])
    return response['message']['content']