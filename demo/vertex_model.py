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

def _initialize_credentials():
    service_account_info = json.loads(_CREDENTIALS_JSON.read_text(encoding="utf-8"))
    project_id = service_account_info["project_id"]

    my_credentials = service_account.Credentials.from_service_account_info(service_account_info)
    aiplatform.init(credentials=my_credentials)
    vertexai.init(project=project_id, location="us-central1")


@cache
def get_model() -> ChatModel:
    _initialize_credentials()
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
