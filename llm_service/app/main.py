from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import json
import requests
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchQuery(BaseModel):
    query: str
    businesses: List[dict]

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Hugging Face API configuration
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_huggingface(payload):
    """Send request to Hugging Face API"""
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.post("/analyze-query")
async def analyze_query(query: SearchQuery):
    try:
        # Format businesses into a string
        businesses_info = "\n".join([
            f"Business: {b['business_name']} (ID: {b['id']})\n" +
            "Services: " + ", ".join([s['name'] for s in b['services']])
            for b in query.businesses
        ])

        # Create the prompt
        prompt = f"""
        User Query: {query.query}
        
        Available Businesses:
        {businesses_info}
        
        Task: Analyze the user query and find matching businesses.
        Return JSON format: {{"matching_ids": [business_ids]}}
        """

        # Query Hugging Face model
        output = query_huggingface({
            "inputs": prompt,
            "parameters": {"max_length": 100, "temperature": 0.7}
        })

        # Process the response
        try:
            if isinstance(output, str):
                result = json.loads(output)
            elif isinstance(output, list) and len(output) > 0:
                result = json.loads(output[0]['generated_text'])
            else:
                raise ValueError("Unexpected response format")
        except json.JSONDecodeError:
            # Fallback: Try to extract JSON from text
            text_response = output[0]['generated_text'] if isinstance(output, list) else str(output)
            import re
            json_match = re.search(r'\{.*\}', text_response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from response")

        # Get matching businesses
        matching_ids = result.get('matching_ids', [])
        matching_businesses = [
            business for business in query.businesses 
            if business['id'] in matching_ids
        ]

        return {
            "matches": matching_businesses
        }

    except Exception as e:
        print(f"Error in analyze_query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "huggingface-bart-large"}