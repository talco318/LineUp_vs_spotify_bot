# ./AI/AI_funcs_gemini.py
import logging

import google.generativeai as genai

from APIs import GEMINI_API
from AI.prompts import prompt


# Create a function to generate responses using Chat GPT API
def generate_response(artists_output: str, weekend_input: str):
    full_prompt = prompt
    full_prompt += f"\nYou have to create a lineup for {weekend_input}.\n The Tomorrowland Festival Lineup for {str(weekend_input)} is:\n" + artists_output
    try:
        genai.configure(api_key=GEMINI_API)

        # Set up the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      # generation_config=generation_config,
                                      safety_settings=safety_settings)
        prompt_parts = [
            "input:" + full_prompt + " ",
            "output: "
        ]
        logging.info("waiting for gemini response......")
        return model.generate_content(prompt_parts).text
    except Exception as e:
        return str(e)
