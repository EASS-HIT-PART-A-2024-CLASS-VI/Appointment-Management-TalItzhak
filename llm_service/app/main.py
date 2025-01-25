from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from openai import OpenAI
import json

class SearchQuery(BaseModel):
    query: str
    businesses: List[dict]

app = FastAPI()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SYSTEM_PROMPT = """You are a semantic service matcher analyzing user requests against available businesses and their services.
Your task is to:
1. Understand the user's intent and requirements
2. Review each business and their services
3. Return ONLY businesses that can truly fulfill the user's needs
4. Return matches as a JSON object with IDs of matching businesses

Example:
User: "I need a haircut"
Businesses:
- Salon A (ID: 1) - Services: Haircut, Color, Style 
- Store B (ID: 2) - Services: Retail, Clothes
Match Response: {"matching_ids": [1]}

Keep responses focused on exact service matches."""

@app.post("/analyze-query")
def analyze_query(query: SearchQuery):
    try:
        businesses_info = "\n".join([
            f"Business: {b['business_name']} (ID: {b['id']})\n" +
            "Services: " + ", ".join([s['name'] for s in b['services']])
            for b in query.businesses
        ])
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Request: {query.query}\n\nAvailable Businesses:\n{businesses_info}"}
            ],
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        matching_businesses = [
            business for business in query.businesses 
            if business['id'] in result.get('matching_ids', [])
        ]
        
        return {
            "keywords": result.get('keywords', []),
            "matches": matching_businesses
        }
        
    except Exception as e:
        print(f"Error in analyze_query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)