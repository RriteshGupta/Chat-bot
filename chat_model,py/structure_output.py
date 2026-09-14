from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from typing import TypedDict,Annotated,Literal,Optional
from pydantic import BaseModel,Field

load_dotenv()





model = ChatOllama(model = "llama3.1")



class Revie(BaseModel):

    summary:str = Field(description="A brif summery of reviwe")
    Sentiment:Literal["prons","neg"] = Field(description="Return sentiment of reviwe either negativ positive or nutral")





structue_model = model.with_structured_output(Revie)

result = structue_model.invoke(""" I was a bit skeptical about the concept behind this show. What saves
 it from banality is just how creative and edgy each episode is.
 The viewer has NO idea what is going to happen next.
   There is no formula and the tension is often ratcheded up to excruciating levels. There are tons of laughs here and the back stories are woven in expertly. So many comedies are played very hammy with lots of stereotypes. 
   This is a very refreshing new form of comedy where the backdrop is more realistic with only some of the characters being over the top. If you're a fan of Louie, The Office or Curb Your Enthusiasm you will likely really love this show. It's fresh and Andy Daly plays the role of the
 hapless reporter to perfection. I hope that we see more hilarious comedies coming. Great stuff!""")
print(result.summary)
print(result.Sentiment)
 