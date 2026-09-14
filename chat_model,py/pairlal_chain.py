from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel



load_dotenv()

promt1 = PromptTemplate(
    template="Describe in full detail of {topic}",
    input_types=['topic']

)

promt2 = PromptTemplate(
    template="tell me about {text} in detail",
    input_variables=['text']
)

promt3 = PromptTemplate(
    template="Give me summery in 10 line of {text}",
    input_variables=['text']
)

model1 = pass
model1 = pass

parser = StrOutputParser()

parlable_chain = RunnableParallel(
    {
        "note":promt1|model1|parser
        "query":promt2|mode2|parser
    }
)

merge_chan = promt3|model1|parser

chain = parlable_chain|merge_chan

chain.invock({'text':text})
