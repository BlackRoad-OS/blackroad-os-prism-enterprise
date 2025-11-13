"""Streamlit entrypoint for the BlackRoad Prism Generator console."""

from __future__ import annotations

import streamlit as st

from prism_console import PRISM_APP

client, api_key = PRISM_APP["create_client"]()

st.set_page_config(**PRISM_APP["page_config"])
st.title(PRISM_APP["metadata"]["title"])

if not api_key:
    st.warning("OpenAI API key not set; responses will be unavailable.")

st.markdown(PRISM_APP["metadata"]["instructions"])

audio_file = st.file_uploader("Upload your voice (mp3 or wav)", type=["mp3", "wav"])
user_input = ""
if audio_file is not None:
    user_input = PRISM_APP["transcribe_audio"](audio_file)
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
