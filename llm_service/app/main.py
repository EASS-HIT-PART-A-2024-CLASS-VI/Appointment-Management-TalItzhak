from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
import json
import requests
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
API_URL = "https://api-inference.huggingface.co/models/gpt2" # Using GPT-2 for text completion
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def create_search_prompt(query: str, businesses: List[dict]) -> str:
    """Create a prompt for the language model"""
    prompt = f"Find businesses that offer services related to '{query}'. Here are the businesses and their services:\n\n"
    
    for business in businesses:
        prompt += f"Business: {business['business_name']}\n"
        prompt += "Services:\n"
        for service in business['services']:
            prompt += f"- {service['name']} (${service['price']}, {service['duration']} minutes)\n"
        prompt += "\n"
    
    prompt += f"\nWhich businesses above offer services related to '{query}'? Return only the business IDs in a JSON format like this: {{\"matching_ids\": [id1, id2]}}."
    return prompt

def find_matching_businesses(query: str, businesses: List[dict]) -> List[int]:
    """Find matching businesses based on the query"""
    query_terms = query.lower().split()
    matching_ids = []
    
    for business in businesses:
        # Check if query matches any service names
        for service in business['services']:
            service_name = service['name'].lower()
            if any(term in service_name for term in query_terms):
                matching_ids.append(business['id'])
                break
    
    return matching_ids

@app.post("/analyze-query")
async def analyze_query(query: SearchQuery):
    try:
        print(f"Received query: {query.query}")  # Debug log
        
        # First, do a basic keyword match
        matching_ids = find_matching_businesses(query.query, query.businesses)
        
        # If we found matches with basic search, return them
        if matching_ids:
            print(f"Found matches through basic search: {matching_ids}")  # Debug log
            return {
                "matches": [
                    business for business in query.businesses 
                    if business['id'] in matching_ids
                ]
            }
        
        # If no basic matches, use HuggingFace API for more advanced matching
        prompt = create_search_prompt(query.query, query.businesses)
        print(f"Sending prompt to HuggingFace: {prompt}")  # Debug log
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
        )
        
        print(f"HuggingFace response: {response.text}")  # Debug log
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error from HuggingFace API"
            )

        # Try to extract JSON from the response
        try:
            result_text = response.json()[0]["generated_text"]
            # Try to find a JSON object in the text
            import re
            json_match = re.search(r'\{.*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                matching_ids = result.get('matching_ids', [])
            else:
                matching_ids = []
        except Exception as e:
            print(f"Error parsing HuggingFace response: {str(e)}")  # Debug log
            # Fallback to basic search if parsing fails
            matching_ids = find_matching_businesses(query.query, query.businesses)

        return {
            "matches": [
                business for business in query.businesses 
                if business['id'] in matching_ids
            ]
        }

    except Exception as e:
        print(f"Error in analyze_query: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "gpt2"}