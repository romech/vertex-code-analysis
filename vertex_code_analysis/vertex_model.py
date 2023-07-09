import json
from functools import cache
from pathlib import Path

import google.cloud.aiplatform as aiplatform
import vertexai
from google.oauth2 import service_account
from vertexai.language_models import InputOutputTextPair
from vertexai.preview.language_models import ChatModel, CodeChatModel
import yaml


_PROJECT_DIR = Path(__file__).parent.parent
_CREDENTIALS_JSON = _PROJECT_DIR / 'service_account.json'
_PROMPT_YAML = _PROJECT_DIR / 'prompt.yaml'
PROMPT_PARAMETERS = {
    "temperature": 0.9,
    "max_output_tokens": 1024,
    "top_p": 1.0,
    "top_k": 40,
}
CONFIDENCE_THRESHOLD = 0.8

def _initialize_credentials(credentials=None):
    if credentials is None:
        credentials = json.loads(_CREDENTIALS_JSON.read_text(encoding="utf-8"))
    project_id = credentials["project_id"]

    my_credentials = service_account.Credentials.from_service_account_info(credentials)
    aiplatform.init(credentials=my_credentials)
    vertexai.init(project=project_id, location="us-central1")


def get_model(credentials=None) -> ChatModel:
    _initialize_credentials(credentials)
    chat_model = ChatModel.from_pretrained("chat-bison")
    return chat_model


@cache
def get_context_prompt() -> str:
    context_dict = yaml.safe_load(_PROMPT_YAML.read_text(encoding="utf-8"))
    return json.dumps(context_dict, indent='\t')
    

def get_prompt_for_user_code(user_code, linenum=True):
    if linenum:
        user_code = _insert_linenum(user_code)
    input_prompt = {
        'task': 'Provide coding tips for this code as you were instructed.',
        'code': user_code
    }
    return json.dumps(input_prompt, indent='\t')

    
def _insert_linenum(source_str):
    lines = source_str.split('\n')
    lines = [f'line {i}:\t{line}' for i, line in enumerate(lines, 1)]
    return '\n'.join(lines)


# def dummy_llm_query(prompt):
#     time.sleep(0.3)
#     comments = [random.choice(['# too short', '# too long', '# too complicated', '# nice'])
#                 for line in prompt.split('\n')]
#     return '\n'.join(comments)
