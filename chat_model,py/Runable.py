from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.runnables import Runnable,RunnableSequence,RunnableParallel
from langchain_core.output_parsers import StrOutputParser

model = ChatOllama(model="llama3.1" )

promt = PromptTemplate(
    template='Write the joke abpout {topic}',
    input_variables=['topic']

)

promt1 = PromptTemplate(
    template='Explain the folloing - {text}',
    input_variables=['text']
)

parser = StrOutputParser()

chain = RunnableSequence(promt,model,parser,promt1,model,parser)


parallel_chain  = RunnableParallel(
    'tweet' : RunnableSequence(promt,model,parser),
    'lionkden':RunnableSequence(promt1,model,parser)
    )

parallel_chain.invoke('topic':'class')

chain.invoke('topic': 'Brothert')




