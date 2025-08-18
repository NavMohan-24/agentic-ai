from typing_extensions import Doc
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from ollama import embeddings
from patch_parser import create_pr_document_from_patch

import os


embeddings = OllamaEmbeddings(model='mxbai-embed-large')
db_location = "./chroma_langchain_db"
directory_path = "./data_diffs"
documents = []
ids = []
add_document = not os.path.exists(db_location)

if add_document:
    
    for i,filenames in enumerate(os.listdir(directory_path)):
        full_path = os.path.join(directory_path,filenames)
        
        with open(full_path,'r') as file:
            patch = file.read()
        
        pagecontent,metadata = create_pr_document_from_patch(patch=patch)
        document = Document(page_content=pagecontent,metadata=metadata,id=str(i))

        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name = "pull_request_tracker",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_document:    
    vector_store.add_documents(documents=documents, ids=ids)


retriever = vector_store.as_retriever(
    search_kwargs = {"k": 3}
)


if __name__ == "__main__":

    query = "GET RECENT CODE CHANGES" 
    diff = retriever.invoke(query)

    print(diff[0].page_content)
