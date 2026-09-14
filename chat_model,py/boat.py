from langchain_ollama import ChatOllama

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage,SystemMessage

import streamlit as st

import tempfile

import subprocess

import soundfile as sf

import sounddevice as sd

load_dotenv()

llm = ChatOllama(model="llama3.1")

model_path = r"C:\Users**\rites\Desktop\langchan model\e**n_US-lessac-medium.onnx"

def speck(text):

        with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f:

                audio_file = f.name

                result = subprocess.run(

                            [

                              "piper",

                              "--model",

                              model_path,

                              "en_US-lessac-medium.onnx",

                              "--output_file",

                            ],

                           check=True

                          input=text.encode(),

                        )

                audio ,rate = sf.read(audio_file)

                sd.play(audio , rate)

                sd.wait()

chat_history = [

    SystemMessage(content='you are helpfull assistence'),

]

st.header("Hey am your Ai model")

st.title("Your Ai")

if "chat_history" not in st.session_state:

     st.session_state.chat_history = []

for message in st.session_state.chat_history:

                if isinstance(message,HumanMessage):

                                     with st.chat_message("usser"):

                                          st.write(message.content)

                elif isinstance(message,AIMessage):

                        with st.chat_message("assistant"):

                                             st.write(message.content)

user_input = st.chat_input('You .')

if user_input is not None:

          st.session_state.chat_history.append(HumanMessage(content=user_input))

          with st.chat_message("user"):

                  st.write(user_input)

          with st.chat_message("assistant"):

                                 placeholder = st.empty()

                                 full_response = ""

                                 sentence = ""

                                 for chunk in llm.stream(st.session_state.chat_history):

                                         text = chunk.content

                                         full_response += text

                                         sentence += text

                                         placeholder.write(full_response)

                                         if any(x in sentence for x in [".","?","!"]):

                                                 speck(sentence.strip())

                                                 sentence = ""

                                         if sentence.strip():

                                                 speck(sentence.strip())

                                                 st.session_state.chat_history.append(AIMessage(content=full_response))