
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import streamlit as st
import tempfile
import subprocess
import soundfile as sf
import sounddevice as sd
import os
import queue
import threading
import base64
import streamlit.components.v1 as components
from avtar import show_avatar


load_dotenv()

llm = ChatOllama(model="llama3.1")



model_path = r"C:\Users\rites\Desktop\langchan model\chat_model,py\voices\en_US-lessac-medium.onnx"

tts_queue = queue.Queue()



def speck(text):
    if not text.strip():
        return

    
    audio_file = os.path.join(tempfile.gettempdir(), "piper_temp_output.wav")
    
    
    command = ['piper', '--model', model_path, '--output_file', audio_file]
    
    try:
        
        result = subprocess.run(command, input=text, text=True, capture_output=True, check=True)
        
        
        if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
            audio, rate = sf.read(audio_file)
            
            sd.play(audio, rate)
            sd.wait() 
        else:
            st.error("🚨 Piper not audio file")
            
    except subprocess.CalledProcessError as e:
        st.error(f"❌ piper comand error: {e.stderr}")
    except Exception as e:
        st.error(f"🚨 somthing is wrong: {e}")



def tts_worker():
    while True:
        text = tts_queue.get()


        if text is None:
            break
        try:
            speck(text)
        except Exception as e:
            print("tts error",e)

        tts_queue.task_done()

if "tts_started" not in st.session_state:

    threading.Thread(
        target=tts_worker,
        daemon = True
    ).start()

    st.session_state.tts_started = True




if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content="You are a helpful assistant.")
    ]


st.header("Hey, I am your AI model")
st.title("Your AI")
show_avatar()

voice = st.toggle("voice")


# पुरानी चैट हिस्ट्री दिखाना
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)


user_input = st.chat_input("You...")

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

            
            if any(x in sentence for x in [".", "?", "!"]):

                if voice:
                   tts_queue.put(
                   speck(sentence.strip())
                   )
                sentence = ""

 
        if sentence.strip():
            tts_queue.put(
            speck(sentence.strip())
            )

        st.session_state.chat_history.append(AIMessage(content=full_response))
