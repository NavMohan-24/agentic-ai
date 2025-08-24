from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ollama import embeddings
from pr_parser import create_documents_from_prs
from pr_fetcher import get_prs_for_release

import os

def ingest_prs_to_db(owner: str, repo: str, token: str):

    """
    Function to ingest data to chroma DB.
    
    Function needs repo details (owner, repo name) as input,
    returns Langchain Document containing details associated with
    all the PRs that merged during the latest release of repo.
    """

    embeddings = OllamaEmbeddings(model='mxbai-embed-large')
    db_location = f"./chroma_db_{owner}_{repo}"

    ids = []
    add_document = not os.path.exists(db_location)

    if add_document:   
        pr_set,version = get_prs_for_release(owner, repo, token)
        documents = create_documents_from_prs(pr_set)

    vector_store = Chroma(
        collection_name = "pull_request_tracker",
        persist_directory=db_location,
        embedding_function=embeddings
    )

    if add_document:    
        vector_store.add_documents(documents=documents, ids=ids)
    
    return vector_store

if __name__ == "__main__":
    owner = "Qiskit"
    repo = "qiskit-addon-aqc-tensor"
    
    with open("token.pat",'r') as file:
        token = file.read()
    
    vector_store = ingest_prs_to_db(owner,repo,token)

    if vector_store:
        print('Completed')
