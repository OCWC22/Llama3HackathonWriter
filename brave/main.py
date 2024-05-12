# search.py
import json
import os
from brave import BraveAPI
from utils import dump_schema

# Create an instance of the BraveAPI class
brave = BraveAPI({
    'subscription_token': os.environ['BRAVE_KEY']
})

# Goggles ID URL
# goggle_id = "https://raw.githubusercontent.com/brave/" \
            # "goggles-quickstart/main/goggles/tech_blogs.goggle"

def search_expert_suggestion_subtopic(subtopic):
    # Setting up parameters
    params = {
        'q': f"Successful people's thoughts on {subtopic}",
        'text_decorations': False,
        # 'freshness': "pw",
        'result_filter': "web",
        # 'goggles_id': goggle_id
    }

    # Performing the search
    results = brave.search(params)

     # Dumping the search results to a JSON file
    with open(f"{subtopic}_search_results.json", "w") as file:
        json.dump(results, file, indent=4)
    # print(results)
    # Dumping and printing the schema of the results
    print(dump_schema(results))

def search_expert_suggestion_subtopic_llm(subtopic):
   # summarizer.py
    import os
    from brave import BraveAPI
    # from main import dump_schema

    # Create an instance of the BraveAPI class
    brave = BraveAPI({
        'subscription_token': os.environ['BRAVE_KEY']
    })

    # Setting up parameters
    params = {
        'q': f"Successful people's tips on {subtopic}, output as JSON",
    }

    # Performing the summarizer search
    results = brave.summarizer(params)
    print(results)


# Dumping and printing the schema of the results
# print(dump_schema(results))


if __name__ == "__main__":
    # print(search_expert_suggestion_subtopic("communication with team members"))
    # print(search_expert_suggestion_subtopic("how to climb corporate ladder as engineer"))
    print(search_expert_suggestion_subtopic("how to host a meeting in tech firm"))






