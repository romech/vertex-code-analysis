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

"""chat_model = ChatModel.from_pretrained("code-bison")
parameters = {
    "temperature": 0.8,
    "max_output_tokens": 1024,
    "top_p": 0.8,
    "top_k": 40,
}
chat = chat_model.start_chat(  # Initialize the chat with model
    # chat context and examples go here
)

# Send the human message to the model and get a response
response = chat.send_message("Are you a human or a machine?", **parameters)
"""

initialization_prompt = dict()
initialization_prompt['context'] = """
You are a very smart Python coding assistant, behaving like an AI linter. You must help the user to improve their code 
by providing short, human-interpretable coding suggestions.
"""
initialization_prompt['instructions'] = """
1. Provide Python coding suggestions that are described in a human-readable language.
2. Each suggestion that you give must be provided in the following format of a JSON file:
`
{
    "line_start": [integer, the start line of your suggestion in the given code, e.g. 3]
    "line_end": [integer, the end line of your suggestion's scope, e.g. 3, 4, 6]. Your suggestions can be multi-line.
    "suggestion": [string, the suggestion that a programmer is supposed to read to improve the code. Preferably one sentence long]
}
`
3. Your output can contain many suggestions.
4. Your output must be parsable with Python json.loads(). 
5. Respond with nothing else but a JSON format string containing N number of suggestions.
6. Your suggestions should not overlap with each other in their scope other or be inside each other.
7. Your suggestions must be associated with the line of code that they try to improve. Make sure that you cite correct 
line numbers.
"""
initialization_prompt['guidelines'] = """
1. Do not overwhelm the user with too many suggestions, but make sure to provide at least some of them so that the 
programmer can always improve.
2. If possible, provide in-built function suggestions or error codes.
3. Examples of improvement could be, e.g. speed improvements, code quality or style improvements, code amount reduction,
potential bug or warning notifications. 
4. Provide short, linter-like suggestions. One sentence preferably.
5. Only provide suggestions that change the code in some way, not make it the same as it was before.
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
initialization_prompt['examples'] = {
    "explanation": "Examples below display how your outputs might look like. Please only use them for guidance purposes and do not use them directly.",
    "example_1": [example_1_input, example_1_output],
    "example_2": [example_2_input, example_2_output],
    "example_3": [example_3_input, example_3_output]
}
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
def performance_test(test_fxn: callable):
    test_completed = False

    total_test_time = 0
    runs = 0

    test_start_time = time.perf_counter()

    while total_test_time < args.total_time:
        try:
            time_delta, _ = test_fxn()
            total_test_time += time_delta
        except Exception as e:
            error_stack = traceback.format_exc()
            return test_completed, error_stack
        runs += 1

    test_completed = True
    average_run_time = (time.perf_counter() - test_start_time) / runs

    return test_completed, average_run_time
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
    "temperature": 0.0,
    "max_output_tokens": 1024,
    "top_p": 0.9,
    "top_k": 40,
}

#code_chat_model = CodeChatModel.from_pretrained("chat-bison")
#chat = code_chat_model.start_chat()

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

print(response)
