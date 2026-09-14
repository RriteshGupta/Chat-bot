from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

model = ChatOllama(model="llama3.1")

lllm = HuggingFaceEndpoint(
    repo_id="TinyLlama-1.1B-Chat-v1.0",
    task="text-generation"
)

model1 = ChatHuggingFace(llm= lllm)

tempalte = PromptTemplate(
    template="Write a detailed report on {topic}",
    input_variables=['topic']

)
tempalte1 = PromptTemplate(
    template="Write a 5 line summery on following text./n {text}",
    input_variables=['text']

)
promt = tempalte.invoke({'topic':'black hole'}) 

result = model.invoke(promt)

print(result.content)

promt1 = tempalte1.invoke({'text':result.content})

result1 = model.invoke(promt1)
print(result1.content)




