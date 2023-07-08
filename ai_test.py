from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel
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

# Why do we even need this?
vertexai.init(project=project_id, location="us-central1")


chat_model = ChatModel.from_pretrained("chat-bison@001")
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
