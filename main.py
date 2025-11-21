"""Streamlit entrypoint for the BlackRoad Prism Generator console."""

from __future__ import annotations

import io

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from prism_console import PRISM_APP
from prism_utils import parse_numeric_prefix


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
def _init_page() -> None:
    """Configure Streamlit and show global metadata."""

    st.set_page_config(**PRISM_APP["page_config"])
    st.title(PRISM_APP["metadata"]["title"])
    st.markdown(PRISM_APP["metadata"]["instructions"])


_init_page()
CLIENT, API_KEY = PRISM_APP["create_client"]()
if not API_KEY:
    st.warning("OpenAI API key not set; responses will be unavailable.")


def _render_hologram(prompt: str) -> None:
    """Render a simple holographic-style projection based on ``prompt``."""

    magnitude = parse_numeric_prefix(prompt)
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = np.sin(np.sqrt(x_grid**2 + y_grid**2)) * magnitude

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x_grid, y_grid, z_grid, cmap="plasma")
    ax.axis("off")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
    buffer.seek(0)
    st.image(buffer, caption="Holographic projection based on your prompt")
    plt.close(fig)


def _collect_user_input() -> str:
    """Return the user's spoken or typed input."""

    audio_file = st.file_uploader("Upload your voice (mp3 or wav)", type=["mp3", "wav"])
    if audio_file is not None:
        transcript = PRISM_APP["transcribe_audio"](audio_file)
        st.markdown(f"**You said:** {transcript}")
        return transcript.strip()

    return st.text_input("Or type here").strip()


user_prompt = _collect_user_input()
if user_prompt:
    if CLIENT is None:
        st.error("OpenAI API key not set.")
    else:
        placeholder = st.empty()
        placeholder.write("Processing request...")
        reply = PRISM_APP["run_completion"](CLIENT, user_prompt, st.session_state)
        placeholder.markdown(f"**Venture Console AI:** {reply}")
        _render_hologram(user_prompt)

st.markdown("---")
st.markdown("**BlackRoad Prism Console** | Live UI Simulation")
st.image(
    "72BF9767-A2EE-4CB6-93F4-4D738108BC4B.png",
    caption="Live Console Interface",
)
