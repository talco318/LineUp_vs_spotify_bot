# ./AI/AI_funcs_claude.py
import anthropic
from prompts import prompt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
claude_api = os.getenv("CLAUDE_API")


# Create a function to generate responses using Chat GPT API
def generate_response(artists_output: str, weekend_input: str):
    full_prompt = prompt
    full_prompt += f"\nTomorrowland Festival Lineup:\n" + artists_output + "\n" + str(weekend_input)
    # print(full_prompt)
    try:

        client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=claude_api,
        )
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2418,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        return message.content
    except Exception as e:
        return str(e)
