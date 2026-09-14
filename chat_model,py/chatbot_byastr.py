import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

import sounddevice as sd
import soundfile as sf
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_ollama import ChatOllama

from avtar import show_avatar


load_dotenv()

st.set_page_config(
    page_title="Your AI",
    page_icon="🤖",
    layout="centered",
)


# Is path ko apne actual folder ke according check karein.
BASE_DIR = Path(
    r"C:\Users\rites\Desktop\langchan model\chat_model,py"
)

MODEL_PATH = BASE_DIR / "voices" / "en_US-lessac-medium.onnx"

PIPER_COMMAND = shutil.which("piper") or shutil.which("piper.exe") or "piper"

llm = ChatOllama(model="llama3.1")

tts_queue = queue.Queue()


def speak(text: str):
    """Piper se speech generate karke play karta hai."""
    if not text or not text.strip():
        return

    if not MODEL_PATH.is_file():
        print(f"Piper model not found: {MODEL_PATH}")
        return

    audio_file = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            audio_file = temp_file.name

        command = [
            PIPER_COMMAND,
            "--model",
            str(MODEL_PATH),
            "--output_file",
            audio_file,
        ]

        subprocess.run(
            command,
            input=text.strip(),
            text=True,
            capture_output=True,
            check=True,
        )

        if not os.path.isfile(audio_file):
            print("Piper ne audio file create nahi ki.")
            return

        if os.path.getsize(audio_file) == 0:
            print("Piper ne empty audio file create ki.")
            return

        audio, rate = sf.read(audio_file, dtype="float32")

        sd.play(audio, rate)
        sd.wait()

    except FileNotFoundError:
        print(
            "Piper command nahi mili. Piper ko PATH me add karein "
            "ya PIPER_COMMAND me full path dein."
        )

    except subprocess.CalledProcessError as error:
        print(f"Piper failed: {error.stderr}")

    except Exception as error:
        print(f"TTS error: {error}")

    finally:
        if audio_file:
            try:
                os.remove(audio_file)
            except OSError:
                pass


def tts_worker():
    while True:
        text = tts_queue.get()

        try:
            if text is None:
                return

            speak(text)

        except Exception as error:
            print(f"TTS worker error: {error}")

        finally:
            tts_queue.task_done()


if "tts_started" not in st.session_state:
    threading.Thread(
        target=tts_worker,
        daemon=True,
    ).start()

    st.session_state.tts_started = True


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(
            content="You are a helpful assistant."
        )
    ]


st.header("Hey, I am your AI model")
st.title("Your AI")

show_avatar()

voice_enabled = st.toggle("Voice")


for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)

    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)


user_input = st.chat_input("You...")


if user_input:
    st.session_state.chat_history.append(
        HumanMessage(content=user_input)
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        sentence_buffer = ""

        for chunk in llm.stream(st.session_state.chat_history):
            text = getattr(chunk, "content", "") or ""

            if not isinstance(text, str):
                text = str(text)

            full_response += text
            sentence_buffer += text

            placeholder.write(full_response)

            while True:
                match = re.search(
                    r"(.+?[.!?])(?:\s+|$)",
                    sentence_buffer,
                    flags=re.DOTALL,
                )

                if not match:
                    break

                completed_sentence = match.group(1).strip()
                sentence_buffer = sentence_buffer[match.end():]

                if voice_enabled:
                    tts_queue.put(completed_sentence)

        if voice_enabled and sentence_buffer.strip():
            tts_queue.put(sentence_buffer.strip())

        st.session_state.chat_history.append(
            AIMessage(content=full_response)
        )