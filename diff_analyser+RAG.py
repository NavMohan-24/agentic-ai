from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Json
from vector import retriever
import json

model = OllamaLLM(model="qwen2.5-coder",temperature=0.1)

template = """
You are an expert in analysing code diff files. 
Your task is to analyze the provided code diff and provide a concise, two-to-three-line summary in natural language.
Do not include any headers, labels, or formatting like JSON. Just provide the summary text.

Here is the  need to analyze and summarize: {diffs}
"""

prompt = ChatPromptTemplate.from_template(template=template)
chain = prompt | model

query = "GET RECENT CODE CHANGES"
docs = retriever.invoke(query)
results = []
for doc in docs:
    diff = doc.page_content
    result = chain.invoke(diff)
    
    results.append(result)


# docs_content = [doc.page_content for doc in docs]
# diffs = "\n\n---\n\n".join(docs_content)
# result = chain.invoke(diffs)
# cleaned_result = result.strip().lstrip("```json\n").rstrip("```")
# parsed_json = json.loads(cleaned_result)
# summary = parsed_json.get("response", "No response found")
# summary = cleaned_result

for res in results:
    print(result)
    print("\n---------------------\n")