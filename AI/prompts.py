# ./AI/prompts.py

prompt_part1 = """
Input Parameters:

1. User's Favorite Artists and Their Song Counts:
Provide a list of your favorite artists and the number of songs you know by each artist. For example:
Yves V: 2 songs
John Newman: 1 song
Martin Jensen: 1 song
Azteck: 4 songs
Maddix: 5 songs

2. Tomorrowland Festival Lineup:
Share the complete lineup for the specified weekend, including the stage/host names, dates, and time slots for each artist's performance. For instance:
Yves V: Placeholder Stage 15, 2024-07-20, 16:00 to 17:00
John Newman: Placeholder Stage 6, 2024-07-19, 18:00 to 19:00
Martin Jensen: Placeholder Stage 9, 2024-07-21, 13:00 to 14:00
Azteck: Placeholder Stage 2, 2024-07-21, 17:00 to 18:00
Maddix: Placeholder Stage 9, 2024-07-28, 15:00 to 16:00

3. Stage Travel Time Data:
The estimated walking time (in minutes) between different stages at the Tomorrowland festival is provided in a separate CSV file named 'walking_time.csv'. This file should be a table where rows and columns represent stages, and the values in the table represent the walking time in minutes between those stages.
"""

with open('../walking_time.csv', 'r') as csvfile:
    walking_time_to_stages = csvfile.read()

prompt_part2 = """
Task Description:
Create a personalized lineup for the Tomorrowland festival based on the provided information. The AI will:

1. Prioritize artists with a higher number of songs in the user's favorites list.
2. Choose the artist with the most songs in the favorites list if multiple artists perform simultaneously.
3. Consider the provided travel time data between stages to optimize the schedule.
4. Suggest meal or drink breaks only when there is a sufficient gap between performances, taking into account travel time between stages.

Note: If the travel time between stages is 0 minutes, do not mention it in the output.

Meal and Break Guidelines:
- Calculate the available gap time by subtracting the end time of the current performance, the travel time to the next stage, and the start time of the next performance.
- Only suggest a meal break if the calculated gap time is at least 90 minutes.
- For calculated gap times between 60 to 89 minutes, suggest a quick snack or refreshment break.
- Do not suggest breaks for calculated gap times shorter than 60 minutes.
- Always include the exact calculated gap time in the break suggestion for transparency.

Output Format:
Generate a personalized schedule for the specified weekend, listing the artists' performances in chronological order. The schedule should include:
- Artist name (and number of songs from the user's list)
- Stage/host name
- Date
- Time slot
- Travel time between stages (when applicable)
- Suggestion for meal, drink, or snack breaks (only when sufficient time is available, including the exact calculated gap time)

The format of the output should be plain text WITHOUT any Markdown.

Example Output:
Personalized Lineup for Tomorrowland Festival:

Day 1:
Maddix (5 songs): Placeholder Stage 8, 19/7, 13:00 to 14:00
Travel Time: 20 minutes to Placeholder Stage 11
John Newman (1 song): Placeholder Stage 11, 19/7, 15:00 to 16:00
Suggestion: You have exactly 100 minutes before the next act (including travel time). This is a great time for a proper meal.

Yves V (2 songs): Placeholder Stage 15, 19/7, 17:30 to 18:30
Travel Time: 15 minutes to Placeholder Stage 9
Suggestion: You have exactly 75 minutes before the next act (including travel time). Consider grabbing a quick snack or refreshment.

Martin Jensen (1 song): Placeholder Stage 9, 19/7, 20:00 to 21:00

Day 2:
Azteck (4 songs): Placeholder Stage 2, 20/7, 14:00 to 15:00
Travel Time: 25 minutes to Placeholder Stage 15
Yves V (2 songs): Placeholder Stage 15, 20/7, 16:00 to 17:00

Additional Constraints and Considerations:
- Always calculate and factor the exact travel time between stages into the personalized schedule to allow sufficient time for moving between performances.
- If an artist show starts 10-20 minutes midnight, add it as to the day it started.
- Ensure that the schedule is realistic and doesn't overbook the user.
- Provide a balanced mix of favorite artists and potential new discoveries.
- Consider the overall flow of the festival experience, including energy levels throughout the day.
- Always prioritize seeing performances over taking breaks when time is limited.
- Double-check all time calculations to ensure accuracy in break suggestions and travel times. Its critical to provide accurate and reliable information to the user.
- Include clear and concise explanations for any break suggestions to help the user understand the reasoning behind the recommendations.


"""

prompt = prompt_part1 + walking_time_to_stages + prompt_part2
