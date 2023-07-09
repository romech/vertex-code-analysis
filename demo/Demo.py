import json
import logging
from pathlib import Path
from operator import itemgetter
from typing import List, Tuple

import streamlit as st
import toolz
from ratelimit import limits
from streamlit_ace import st_ace

import vertex_model


st.set_page_config(
    page_title="Vertex Code Analyser",
    page_icon="✍️",
    layout="wide",
)


@st.cache_data
def get_code_examples():
    example_paths = sorted((Path(__file__).parent / 'poor_code_examples').glob('*.py'))
    examples = {'blank': ''}
    examples.update({path.stem: path.read_text() for path in example_paths})
    return examples
    

@st.cache_resource
def get_model():
    return vertex_model.get_model()


class Assistant:
    def __init__(self):
        if 'query_history' not in st.session_state:
            st.session_state['query_history'] = {}
        self.model = get_model()
        
    def update_suggestion(self, user_code):
        cached_result = st.session_state['query_history'].get(user_code)
        if cached_result is not None:
            logging.debug('cache hit')
            self._update_output_widget(cached_result)
            return
        
        self._query_and_update(user_code)
    
    def _query_and_update(self, user_code):
        with ai_side:
            with st.spinner('Prompting...'):
                response = self.query_llm(user_code)
                if response is None:
                    logging.info('Rate limit exceeded')
                    return
        self._cache_reponse(user_code, response)
        self._update_output_widget(response)
    
    @limits(calls=10, period=1, raise_on_limit=False)
    def query_llm(self, user_code) -> Tuple[str, List[dict]]:
        if user_code == '':
            return '', []
        chat = self.model.start_chat(
            context=vertex_model.get_context_prompt(),
            **vertex_model.PROMPT_PARAMETERS)
        
        prompt = vertex_model.get_prompt_for_user_code(user_code)
        response_struct = chat.send_message(prompt)
        response_text = response_struct.text
        try:
            response = json.loads(response_text, strict=False)
            response = response['suggestions']
            last_response.json(response)
            suggestions = self._parse_response(user_code, response)
        except:
            logging.exception('Failed to parse response')
            last_response.markdown(
                f"""
                Failed to parse response. See console output for error details.
                ```
                {response_text}
                ```
                """.strip('\n'))
            return '...', []
            
        return suggestions

    def _parse_response(self, user_code: str, response: dict) -> str:
        total_lines = user_code.count('\n') + 1
        get_confidence = itemgetter('confidence')
        suggestions_per_line = toolz.groupby('code_line_num', response)
        best_suggestion_per_line = toolz.valmap(lambda b: max(b, key=get_confidence),
                                                suggestions_per_line)
        best_suggestion_per_line = toolz.valfilter(lambda b: get_confidence(b) >= 0.8,
                                                   best_suggestion_per_line)
        ranked_suggestions = sorted(best_suggestion_per_line.values(),
                                    key=get_confidence,
                                    reverse=True)
        
        comments = [''] * total_lines
        notifications = []
        for block in ranked_suggestions:
            line_num = block['code_line_num'] - 1
            if line_num >= total_lines:
                logging.warning(f'line {line_num} is out of range')
                last_status.write('Encountered invalid line number')
                continue
            suggestion = block.get('replacement_code', '').strip('\n')
            
            suggestion_lines = suggestion.split('\n')
            # checking if the suggestion is longer than the input
            if (extra_lines := len(suggestion_lines) + line_num - total_lines) > 0:
                comments += [''] * (extra_lines)
            # checking for multi-line overlaps
            if any(comments[line_num + offset] != ''
                   for offset in range(len(suggestion_lines))):
                # found overlapping suggestion
                continue
            
            for i, line in enumerate(suggestion_lines, line_num):
                comments[i] = line
            
            explanation = block.get('explanation', '').replace('\n',' ')
            notifications.append({
                "row": line_num,
                "column": 0,
                "text": explanation,
                "type": self._parse_suggestion_type(block)
            })
            if explanation:
                if line_num > 0 and comments[line_num - 1] == '':
                    comments[line_num - 1] = f'# {explanation}'
            #     else:
            #         comments[line_num] += f'  # {explanation}'
        return '\n'.join(comments), notifications
    
    def _update_output_widget(self, suggestions):
        logging.debug('updating response')
        text, notifications = suggestions
        with ai_code_placeholder:
            st.session_state['last_response'] = text
            st.session_state['last_notifications'] = notifications
            st_ace(value=text,
                   language=language,
                   readonly=True,
                   auto_update=True,
                   annotations=notifications)
            
    def _cache_reponse(self, user_code, response):
        hist = st.session_state['query_history']
        hist[user_code] = response
        st.session_state['query_history'] = hist
    
    @classmethod
    def _parse_suggestion_type(cls, suggestion_block):
        match suggestion_block['suggestion_class_number']:
            case 3:
                return 'warning'
            case 4:
                return 'error'
            case _:
                return 'info'


assistant = Assistant()

# PAGE LAYOUT

st.write("# Welcome to Vertex Code Analyser! 👋")

with st.sidebar:
    st.image('https://developers.google.com/static/focus/images/palm-logo.svg', width=128)
    code_examples = get_code_examples()
    code_example_name = st.selectbox(label='Try out examples',
                                     options=code_examples.keys())
    
    language = st.selectbox(label='Language',
                            options=['python', 'js', 'go', 'java', 'sql', 'ts'],
                            disabled=True)
    auto_suggest = st.checkbox(label='Auto-suggest', value=False)

editor_side, ai_side = st.columns([0.5, 0.5])


with ai_side:
    st.write('AI suggestions will apear here')
    ai_code_placeholder = st.empty()
    with ai_code_placeholder:
        st_ace(
            value=st.session_state.get('last_response', ''),
            language=language,
            readonly=True,
            auto_update=True,
            annotations=st.session_state.get('last_notifications', None),
            key='response')

with editor_side:
    st.write('Try out your code:')
    user_code = st_ace(value=code_examples[code_example_name],
                       language=language,
                       auto_update=auto_suggest,
                       max_lines=300,
                       key=f'user_code_{code_example_name}')

with st.expander('Debug info'):
    last_status = st.empty()
    last_response = st.empty()

assistant.update_suggestion(user_code)
