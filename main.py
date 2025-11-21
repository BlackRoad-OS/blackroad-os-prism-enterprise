"""Streamlit entrypoint for the BlackRoad Prism Generator console."""

from __future__ import annotations
"""Streamlit console for the BlackRoad Prism holographic assistant."""

from __future__ import annotations
"""Streamlit app for the BlackRoad Prism Generator with GPT and voice input."""

import io
import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from prism_console import PRISM_APP
import whisper
from openai import OpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile

from prism_utils import parse_numeric_prefix

st.set_page_config(layout="wide")
st.title("BlackRoad Prism Generator with GPT + Voice Console")

_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key) if _api_key else None
# Instantiate the OpenAI client only when an API key is available so the
# module can still import and Streamlit can display a friendly warning instead
# of crashing at startup.
# Configure the OpenAI client only when an API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key) if openai_api_key else None
if client is None:
    st.warning("OpenAI API key not set. Set OPENAI_API_KEY to enable responses.")

client, api_key = PRISM_APP["create_client"]()

from prism_utils import parse_numeric_prefix

"""Streamlit app for the BlackRoad Prism Generator with GPT and voice input."""

st.set_page_config(layout="wide")
st.title("BlackRoad Prism Generator with GPT + Voice Console")

# Configure OpenAI client
_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key) if _api_key else None
if client is None:
    st.warning("OpenAI API key not set. Set OPENAI_API_KEY to enable responses.")


st.set_page_config(**PRISM_APP["page_config"])
st.title(PRISM_APP["metadata"]["title"])
@st.cache_resource
def get_whisper_model():
    """Load and cache the Whisper model so repeated runs stay responsive."""

    """Load and cache the Whisper model."""
    return whisper.load_model("base")


def transcribe_audio(uploaded_file: UploadedFile) -> str:
    """Transcribe an uploaded audio clip using Whisper."""

    suffix = os.path.splitext(uploaded_file.name)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        model = get_whisper_model()
        result = model.transcribe(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return result["text"]

if not api_key:
    st.warning("OpenAI API key not set; responses will be unavailable.")

st.markdown(PRISM_APP["metadata"]["instructions"])
    """Transcribe an uploaded audio file using Whisper."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    try:
        model = get_whisper_model()
        result = model.transcribe(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return result["text"]


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": (
                "You are the BlackRoad Venture Console AI, a holographic assistant that "
                "replies with scientific and symbolic insights."
            ),
        }
    ]

st.markdown(
    "#### Speak or type an idea, formula, or question. The AI will respond and project a hologram:"
)

audio_file = st.file_uploader("Upload your voice (mp3 or wav)", type=["mp3", "wav"])
user_input = ""
if audio_file is not None:
    user_input = PRISM_APP["transcribe_audio"](audio_file)
if audio_file is not None:
    user_input = transcribe_audio(audio_file)
    st.markdown(f"**You said:** {user_input}")
else:
    user_input = st.text_input("Or type here")

if user_input:
    if not client:
        st.error("OpenAI API key not set.")
    else:
        placeholder = st.empty()
        placeholder.write("Processing request...")
        reply = PRISM_APP["run_completion"](client, user_input, st.session_state)
        placeholder.markdown(f"**AI:** {reply}")
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.chat_history,
        )
        assistant_reply = response.choices[0].message.content
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.markdown(f"**Venture Console AI:** {assistant_reply}")

        magnitude = parse_numeric_prefix(user_input)
        fig = plt.figure(figsize=(6, 4))
        ax = fig.add_subplot(111, projection="3d")
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x**2 + y**2)) * magnitude
        ax.plot_surface(x, y, z, cmap="plasma")
        ax.axis("off")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        buf.seek(0)
        st.image(buf, caption="Holographic projection based on your prompt")
        st.image(buf)
        plt.close(fig)

st.markdown("---")
st.markdown("**BlackRoad Prism Console** | Live UI Simulation")
st.image("72BF9767-A2EE-4CB6-93F4-4D738108BC4B.png", caption="Live Console Interface")
        placeholder = st.empty()
        placeholder.write("Processing request...")
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=st.session_state.chat_history
        )
        reply = response.choices[0].message["content"]
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        placeholder.markdown(f"**AI:** {reply}")
