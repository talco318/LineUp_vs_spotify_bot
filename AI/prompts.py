# ./AI/prompts.py

prompt_part1 = """
Input Parameters:

  User's Favorite Artists and Their Song Counts:
    Provide a list of your favorite artists and the number of songs you know by each artist. 
    For example:

      Yves V: 2 songs
      John Newman: 1 song
      Martin Jensen: 1 song
      Azteck: 4 songs
      Maddix: 5 songs

  Tomorrowland Festival Lineup:
    Share the complete lineup for the specified weekend, including the stage/host names, dates, and time slots for each artist's performance. 
    For instance:

      Yves V: Placeholder Stage 15, 2024-07-20, 16:00 to 17:00
      John Newman: Placeholder Stage 6, 2024-07-19, 18:00 to 19:00
      Martin Jensen: Placeholder Stage 9, 2024-07-21, 13:00 to 14:00
      Azteck: Placeholder Stage 2, 2024-07-21, 17:00 to 18:00
      Maddix: Placeholder Stage 9, 2024-07-28, 15:00 to 16:00

  Stage Travel Time Data:
    The estimated walking time (in minutes) between different stages at the Tomorrowland festival is provided in a separate CSV file named 'walking_time.csv'. 
    This file should be a table where rows and columns represent stages, and the values in the table represent the walking time in minutes between those stages. 
"""

with open('../walking_time.csv', 'r') as csvfile:
    walking_time_to_stages = csvfile.read()

prompt_part2 = """
Task Description:

  You will create a personalized lineup for you for the Tomorrowland festival. 
  The AI will prioritize artists with a higher number of songs in your favorites list. 
  If multiple artists perform simultaneously, the AI will choose the artist with the most songs in your favorites.

  - For artists with fewer than 5 songs in your favorites, the AI can suggest a suitable time for a meal or drink break instead of their performance.

  - Additionally, it will consider the provided travel time data between stages to optimize your schedule and incorporate suggestions for meal or drink breaks during the festival.

Output Format:

  You will generate a personalized schedule for the specified weekend, listing the artists' performances in chronological order. 
  The schedule will include:

    - Artist name (and number of songs from your list)
    - Stage/host name
    - Date
    - Time slot
    - Travel time between stages (when applicable)
    - Suggestion for meal or drink breaks (if applicable)

  The format of your output will be plain text without any Markdown.

Example:

  Personalized Lineup for Tomorrowland Festival:

  Day 1:

    Maddix (5 songs): Placeholder Stage 8, 19/7, 13:00 to 14:00
    [Travel Time: x minutes to Placeholder Stage 11]
    John Newman (1 song): Placeholder Stage 11, 19/7, 14:15 to 15:15
    Suggestion: This could be a great time for dinner (6PM-9PM).

  Day 2:

    Yves V (2 songs): Placeholder Stage 15, 20/7, 16:00 to 17:00
    Suggestion: This could be a great time for lunch (1PM-5PM).
    Martin Jensen (1 song): Placeholder Stage 9, 20/7, 18:00 to 19:00
    [Travel Time: y minutes]
    Yves V (2 songs): Placeholder Stage 15, 20/7, 19:00 to 20:00
    etc.


  Day 3:
  
    Azteck (8 songs): Placeholder Stage 15, 21/7, 15:00 to 16:00
    Suggestion: This could be a great time for lunch (11AM-2PM).
    Martin Jensen (12 song): Placeholder Stage 9, 21/7, 18:00 to 19:00
    [Travel Time: y minutes]
    Moshe Moshe (41 songs): Placeholder Stage 15, 21/7, 19:00 to 20:00
    etc.

Additional Constraints and Considerations:
The travel time between stages should be factored into the personalized schedule to allow sufficient time for moving between performances.
"""

prompt = prompt_part1 + walking_time_to_stages + prompt_part2
