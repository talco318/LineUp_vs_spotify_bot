# ./AI/AI_funcs_gemini.py
import logging
import json
import re

import google.generativeai as genai
from AI.prompts import prompt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
gemini_api = os.getenv("GEMINI_API")


def clean_json_response(response_text: str) -> str:
    """Clean the response to extract valid JSON."""
    # Remove markdown code blocks if present
    text = response_text.strip()

    # Remove ```json and ``` markers
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    # Find JSON object boundaries
    start_idx = text.find('{')
    end_idx = text.rfind('}')

    if start_idx != -1 and end_idx != -1:
        text = text[start_idx:end_idx + 1]

    return text


def generate_response(artists_output: str, weekend_input: str) -> str:
    """Generate a JSON lineup response using Gemini API."""
    full_prompt = prompt
    full_prompt += f"\n\nCREATE LINEUP FOR: {weekend_input}\n"
    full_prompt += f"USER'S ARTISTS FROM PLAYLIST:\n{artists_output}\n"
    full_prompt += "\nRemember: Return ONLY valid JSON, no markdown, no extra text."

    try:
        genai.configure(api_key=gemini_api)

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            safety_settings=safety_settings
        )

        logging.info("Waiting for Gemini response...")
        response = model.generate_content(full_prompt)
        response_text = response.text

        # Clean and validate JSON
        cleaned_json = clean_json_response(response_text)

        # Validate it's proper JSON
        try:
            json.loads(cleaned_json)
            logging.info("Valid JSON response received from Gemini")
            return cleaned_json
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON from Gemini: {e}")
            logging.error(f"Raw response: {response_text[:500]}")
            # Return a fallback JSON structure
            return json.dumps({
                "days": [],
                "tips": ["Could not parse AI response. Please try again."],
                "total_artists": 0,
                "total_shows": 0,
                "raw_response": response_text
            })

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return json.dumps({
            "days": [],
            "tips": [f"Error: {str(e)}"],
            "total_artists": 0,
            "total_shows": 0,
            "error": str(e)
        })
