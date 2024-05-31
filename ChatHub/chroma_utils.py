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


def summary(conversation_string):

    prompt_template = ChatPromptTemplate.from_template(prompt_summarize)
    prompt = prompt_template.format(context=conversation_string)

    response = ollama.chat(model='strangex/saraa-8b-orpo-aunqa', messages=[
    {
        'role': 'user',
        'content': prompt,
    },
    ])
    return response['message']['content']

