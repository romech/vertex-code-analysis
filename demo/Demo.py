import random
import time

import streamlit as st
from streamlit_ace import st_ace

st.set_page_config(
    page_title="Vertex Code Analyser",
    page_icon="✍️",
    layout="wide",
)

def update_ai_suggestions(text):
    with ai_code_placeholder:
        st_ace(value=text,
               language='python',
               readonly=True,
               auto_update=True)
        
def query_llm():
    time.sleep(0.3)
    comments = [random.choice(['# too short', '# too long', '# too complicated', '# nice'])
                for line in user_code.split('\n')]
    return '\n'.join(comments)

# PAGE LAYOUT

st.write("# Welcome to Vertex Code Analyser! 👋")

with st.sidebar:
    language = st.selectbox(label='Language', options=['python', 'js', 'c', 'cpp', 'go', 'java', 'rust'])
    auto_suggest = st.checkbox(label='Auto-suggest', value=False)

editor_side, ai_side = st.columns([0.6, 0.4])

with editor_side:
    st.write('Try out your code:')
    user_code = st_ace(language=language,
                       auto_update=auto_suggest,
                       max_lines=300,
                       key='user_code')


with ai_side:
    st.write('AI suggestions will apear here')
    ai_code_placeholder = st.empty()
    with st.spinner('Prompting...'):
        ai_comments = query_llm()
    update_ai_suggestions(ai_comments)
