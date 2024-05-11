# search.py
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
        'q': f"Successful people's tips on {subtopic}",
        'text_decorations': False,
        # 'freshness': "pw",
        'result_filter': "web",
        # 'goggles_id': goggle_id
    }

    # Performing the search
    results = brave.search(params)
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
    print(search_expert_suggestion_subtopic_llm("Communication with team members"))



