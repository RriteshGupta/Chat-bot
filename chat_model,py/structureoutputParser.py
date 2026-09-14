from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser


model = ChatOllama(model="llama3.1")

lllm = HuggingFaceEndpoint(
    repo_id="TinyLlama-1.1B-Chat-v1.0",
    task="text-generation"
)

model1 = ChatHuggingFace(llm= lllm)

parser = StrOutputParser()

template1 = property(
    template = 'Give me 3 fact about {place} /n {formet_instruction}',
    input_variables = ['place'],
    parcial_variables = {'formet_instruction', parser.get_format_instructions()}


)

promt = template1.invoke({'place':'india'})

chain = template1 | model | parser

result = chain.invoke(promt)
print(result.content)



    

print(promt)

