from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
from vertexai.language_models import InputOutputTextPair
from vertexai.preview.language_models import ChatModel, CodeChatModel
import vertexai
import json

# Load the service account json file
# Update the values in the json file with your own
with open(
    "service_account.json"
) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
    service_account_info = json.load(f)

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

# Initialize Google AI Platform with project details and credentials
aiplatform.init(
    credentials=my_credentials,
)

with open("service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]


# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")

initialization_prompt = dict()
initialization_prompt['context'] = """
You are a very smart Python coding assistant, behaving like an AI linter. You must help the user to improve their code 
by providing short, human-interpretable coding suggestions that improve code speed, quality and correctness.
"""
initialization_prompt['instructions'] = """
1. Provide Python coding suggestions that are described in a human-readable language.
2. For each line of code please provide the following JSON field of suggestion:
`
{
    "code_line_num": [int, which line of code the suggestion is dedicated to]
    "suggestion": [string; the suggestion that a programmer is supposed to read to improve the code. Preferably one sentence long]
    "confidence": [float; confidence score in range of [0, 1] displaying your confidence that your suggestion is useful] 
    "suggestion_class_number": [integer; improvement regarding: 0- code performance or program; 1: code quality; 2: style or convention compliance; 3: warning for bug / bad practice; 4: error / bug fix; 5: other]
}
`
3. Your output can contain many suggestions.
4. Respond with nothing else but a JSON format string containing N number of suggestions. It must be parsable with Python json.loads().
5. Your suggestions must not overlap with each other in their scope other and not be inside each other.
6. Your suggestions must be associated with the line of code that they try to improve. Make sure that you cite correct 
line numbers.
"""
initialization_prompt['guidelines'] = """
1. Make sure to provide at least some suggestions for the code input snippet so that the programmer can always improve.
2. If possible, provide in-built function suggestions or error codes.
3. Provide short, linter-like suggestions. Preferably one sentence long.
4. Only provide suggestions that change the code in some way, not make it the same as it was before.
5. Your suggestion should provide a clear instruction of how the code needs to be changed.
6. IMPORTANT: Be absolutely sure that your suggestion is useful.
"""

example_1_input = """
`
line 1: def AI_model_test(test_model: Callable):
line 2:     test_completed = False
line ...: ...
line 24:    return passed_or_not, time_it_took
`
"""
example_1_output = """
{
    "line_start": 1,
    "line_end": 1,
    "suggestion:" "Use `-> Tuple[bool, float]` for the return type-hint"
}
"""
example_2_input = """
`
line 32: time_threshold = 5
`
"""
example_2_output = """
{
    "line_start": 32,
    "line_end": 32,
    "suggestion:" "Express time in float format as it is a fractional number"
}
"""
example_3_input = """
`
line 32: integers = [5, 8, 3]
line 33: total = 0
line 34: for element in integers:
line 35:    total += element
`
"""
example_3_output = """
{
    "line_start": 32,
    "line_end": 35,
    "suggestion:" "Use Python in-built `sum` function: `total = sum(integers)` for faster performance and readability"
}
"""
#initialization_prompt['examples'] = {
#    "explanation": "Examples below display how your outputs might look like. Please only use them for guidance purposes and do not use them directly.",
#    "example_1": [example_1_input, example_1_output],
#    "example_2": [example_2_input, example_2_output],
#    "example_3": [example_3_input, example_3_output]
#}
#example_prompt['examples'] = [
#    InputOutputTextPair(
#        input_text=example_1_input,
#        output_text=example_1_output
#    )
#]



input_prompt = dict()

input_prompt["task"] = """
Provide coding tips for this code as you were instructed.
"""
input_prompt["code"] = '''
def get_project_root(root_folder: str = 'CoderAgentGPT') -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    while dir_path != '/':
        if Path(dir_path).name == root_folder:
            return dir_path
        else:
            dir_path = os.path.dirname(dir_path)

    raise Exception('Project root not found.')
'''

def insert_linenum(source_str, target_str='\n'):
    count = 1
    result = ""
    splits = source_str.split(target_str)

    for part in splits[:-1]:
        result += part + target_str + "line " + str(count) + ": "
        count += 1

    result += splits[-1]  # append the last part without any addition
    return result

input_prompt['code'] = insert_linenum(input_prompt['code'])

#parameters = {
#    "temperature": 0.0,  # Temperature controls the degree of randomness in token selection.
#    "max_output_tokens": 1024,  # Token limit determines the maximum amount of text output.
#}

parameters = {
    "temperature": 0.9,
    "max_output_tokens": 1024,
    "top_p": 1.0,
    "top_k": 40,
}

#code_chat_model = CodeChatModel.from_pretrained("chat-bison")
#chat = code_chat_model.start_chat()

# import yaml

# with open('prompt.yaml', 'w') as f:
#     yaml.dump(initialization_prompt, f, indent=4, sort_keys=False,)
    
chat_model = ChatModel.from_pretrained("chat-bison")
chat = chat_model.start_chat(
    context=json.dumps(initialization_prompt)
)

# Initialize
#_ = chat.send_message(
#    json.dumps(initialization_prompt), **parameters
#)

response = chat.send_message(
    json.dumps(input_prompt), **parameters
)
a = 5