# ./AI/prompts.py
# TODO: Improve the prompt for 2 weekends case.
prompt_part1 = """
Input Parameters:

User's Favorite Artists and Their Song Counts: Provide a list of your favorite artists and the number of songs you know by each artist. For example:
Yves V: 2 songs
John Newman: 1 song
Martin Jensen: 1 song
Azteck: 4 songs
Maddix: 5 songs
etc. 

Tomorrowland Festival Lineup: Share the complete lineup for the specified weekend, including the stage/host names, dates, and time slots for each artist's performance. For instance:
Yves V: Placeholder Stage 15, 2024-07-20, 16:00 to 17:00
John Newman: Placeholder Stage 6, 2024-07-19, 18:00 to 19:00
Martin Jensen: Placeholder Stage 9, 2024-07-21, 13:00 to 14:00
Azteck: Placeholder Stage 2, 2024-07-21, 17:00 to 18:00
Maddix: Placeholder Stage 9, 2024-07-28, 15:00 to 16:00
etc.

Stage Travel Time Data: The estimated walking time (in minutes) between different stages at the Tomorrowland festival is provided in the following table:
"""

with open('../walking_time.csv', 'r') as csvfile:
    walking_time_to_stages = csvfile.read()



prompt_part2 = """
Task Description:
You will create a personalized lineup for you for Tomorrowland festival. It will prioritize artists with a higher number of songs in your favorites list. If multiple artists perform simultaneously, the AI will suggest the artist with the most songs in your favorites. For artists with fewer than 5 songs in your favorites, the AI will suggest a suitable time for a meal or drink break instead of their performance. Additionally, it will consider the provided travel time data between stages and incorporate suggestions for meal or drink breaks during the festival.
Output Format:
You will generate a personalized schedule for the specified weekend, listing the artists performances in order, along with their stage/host names, dates, time slots, and the number of songs you know by each artist. For artists with fewer than 5 songs in your favorites or if there is a gap in the schedule, you can suggest a time for a meal based on typical meal times (Breakfast:7AM- 10AM, Lunch:11AM-2PM, Dinner:6PM-9PM) or drink break instead of their performance. You will also factor in the walking time between stages when i will provide.
The format of your output will be WITHOUT any Markdown! Please provide the output in plain text format.
Example:

Personalized Lineup for Tomorrowland Festival:
day 1:
1. Maddix (5 songs): Placeholder Stage 8, 19/7, 13:00 to 14:00
2. [Travel Time: x minutes] 
etc.

day 2:
1. Yves V (2 songs): Placeholder Stage 15, 20/7, 16:00 to 17:00
2. Suggestion: This could be a great time for lunch (11AM-2PM).
3. Martin Jensen (1 song): Placeholder Stage 9, 20/7, 18:00 to 19:00
4. [Travel Time: y minutes]
5. Yves V (2 songs): Placeholder Stage 15, 20/7, 19:00 to 20:00
etc.

day 3:
1. Azteck (8 songs): Placeholder Stage 15, 21/7, 15:00 to 16:00
2. Suggestion: This could be a great time for lunch (11AM-2PM).
3. Martin Jensen (12 song): Placeholder Stage 9, 21/7, 18:00 to 19:00
4. [Travel Time: y minutes]
5. Moshe Moshe (41 songs): Placeholder Stage 15, 21/7, 19:00 to 20:00
etc.

Additional Constraints and Considerations:
The travel time between stages should be factored into the personalized schedule to allow sufficient time for moving between performances.
"""


prompt = prompt_part1 + walking_time_to_stages + prompt_part2

