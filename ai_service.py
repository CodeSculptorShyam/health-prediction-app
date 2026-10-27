
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent"
)


def generate_health_remark(glucose, haemoglobin, cholesterol):
    if not API_KEY:
        logging.error("GEMINI_API_KEY is not configured.")
        return "AI remarks unavailable: configure the Gemini API key."

    prompt = f"""
    You are an automated medical reporting assistant. Given three lab metrics (Glucose, Haemoglobin, Cholesterol), write a single-paragraph remark highlighting key abnormalities, disease risks, and normal findings.

    Example Input:
    Glucose: 232 mg/dL, Haemoglobin: 13.5 g/dL, Cholesterol: 180 mg/dL

    Example Output:
    Based on the provided lab parameters, the evaluation reveals significant hyperglycemia driven by a high blood glucose level of 232 mg/dL, pointing to a potential risk for or presence of Diabetes Mellitus that requires confirmation through an HbA1c test; meanwhile, both haemoglobin (13.5 g/dL) and total cholesterol (180 mg/dL) lie within normal reference ranges, showing no immediate clinical abnormalities.

    ---
    Now generate the single-paragraph remark for these input values:
    Glucose: {glucose} mg/dL
    Haemoglobin: {haemoglobin} g/dL
    Cholesterol: {cholesterol} mg/dL
    """


    headers = {
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 400,
        },
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        remark = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        if not remark:
            raise ValueError("The AI returned an empty response.")

        return remark

    except (requests.RequestException, ValueError, KeyError, IndexError):
        logging.exception("Gemini AI remark generation failed")
        return (
            "AI remarks could not be generated. "
            "Check the application terminal."
        )
