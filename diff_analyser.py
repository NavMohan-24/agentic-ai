from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="qwen2.5-coder")

template = """
You are an expert in analysing code diff files. 
You can understand what changes happened in a codebase by analysing the diff files and summarize it in Natural Language.
You will return the summary in two or three line.

Here is the diff file you need to analyse and summarize: {diff}
"""

with open('test_diff.txt','r') as file:
    diff = file.read()

prompt = ChatPromptTemplate.from_template(template=template)
chain = prompt | model


result = chain.invoke(diff)

print(result)