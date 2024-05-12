import os
import json
from groq import Groq

# Safe way to access the environment variable
api_key = os.getenv("GROQ_API_KEY")
if api_key is None:
    raise ValueError("GROQ_API_KEY is not set in the environment")

# Initialize the Groq client
client = Groq(api_key=api_key)

# Safely load the JSON data from a file
try:
    with open("./data/comm.json", 'r') as file:
        comm = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError("The file 'comm.json' does not exist in the ./data directory")
except json.JSONDecodeError:
    raise ValueError("The file 'comm.json' is not a valid JSON file")
print(json.dumps(comm))
# Creating chat completions with the Groq API
try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"backfill the people field of each empty record with best possible guess and output the same json array {json.dumps(comm)}, output ONLY json without any other text",
            }
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"},
    )
    
    # Extract the JSON output directly from the response
    print(chat_completion.choices[0].message.content)
    output_json = json.loads(chat_completion.choices[0].message.content)

    # Write the output JSON to a file
    with open('./data/output.json', 'w') as outfile:
        json.dump(output_json, outfile, indent=4)
    print("Output successfully written to './data/output.json'")

except Exception as e:
    print(f"An error occurred while fetching chat completions or writing the file: {str(e)}")

