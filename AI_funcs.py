import anthropic
from APIs import Claude_api
prompt = """
Enhanced Prompt for Personalized Tomorrowland Festival Lineup

Input Parameters:

1. Weekend Number: Please specify the weekend number for the Tomorrowland festival (e.g., 1, 2).

2. Favorite Artists and Their Song Counts:
   - For each artist you enjoy, provide their name along with the number of songs you know by that artist. Feel free to include as many artists as you'd like. For example:
     - Tiësto: 15 songs
     - Lost Frequencies: 10 songs
     - Armin van Buuren: 20 songs
     - ...

3. Tomorrowland Festival Lineup:
   - Share the complete lineup for the specified weekend. Include the names of all artists performing and their respective time slots. For instance:
     - Tiësto: Placeholder Stage 14, 2024-07-28, 14:00 to 15:00
     - Lost Frequencies: LOST FREQUENCIES & FRIENDS, 2024-07-20, 12:00 to 13:00
     - Armin van Buuren: Placeholder Stage 2, 2024-07-19, 12:00 to 13:00
     - ...

Output:
Based on the provided details, the AI platform will meticulously curate a personalized lineup for you to immerse yourself in during the Tomorrowland festival. If multiple artists perform simultaneously, the AI will prioritize the artist with a higher number of songs in your favorites list. Additionally, it will consider the overall popularity, genre preferences, and time slots to craft an unforgettable musical journey.
"""

# Create a function to generate responses using Chat GPT API
def generate_response(prompt):
    try:

        client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=Claude_api,
        )
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    weekend_input = 'weekend 1'
    artists_input = """
Tiësto- Songs number: 1
Show:
weekend 2
Stage and host name: Placeholder Stage 14
Date: 2024-07-28 14:00 to 2024-07-28 15:00

Lost Frequencies- Songs number: 1
Show:
weekend 1
Stage and host name: LOST FREQUENCIES & FRIENDS
Date: 2024-07-20 12:00 to 2024-07-20 13:00
Show2:
weekend 2
Stage and host name: Placeholder Stage 9
Date: 2024-07-26 12:00 to 2024-07-26 13:00

Armin van Buuren- Songs number: 1
Show:
weekend 1
Stage and host name: Placeholder Stage 2
Date: 2024-07-19 12:00 to 2024-07-19 13:00
Show2:
weekend 2
Stage and host name: Placeholder Stage 1
Date: 2024-07-27 18:00 to 2024-07-27 19:00"""

    full_prompt = f"\nTomorrowland Festival Lineup:\n{artists_input}"
    full_prompt += weekend_input

    response = generate_response(full_prompt)
    print(response[0].text)