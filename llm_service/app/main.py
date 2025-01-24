from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import os
from openai import AsyncOpenAI

class SearchQuery(BaseModel):
    query: str
    businesses: List[dict]

app = FastAPI()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYSTEM_PROMPT = """You are a semantic service matcher. Extract only the most relevant keywords from user queries and match them to businesses.
Examples:
Query: "i want to buy birthday cake to my son"
Keywords: cake
Query: "fix my phone screen"
Keywords: phone, screen
Return response format:
{
    "keywords": ["word1", "word2"],
    "matching_ids": [1, 2]
}"""

@app.post("/analyze-query")
async def analyze_query(query: SearchQuery):
    try:
        businesses_info = "\n".join([
            f"Business: {b['business_name']} (ID: {b['id']})\n" +
            "Services: " + ", ".join([s['name'] for s in b['services']])
            for b in query.businesses
        ])
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Request: {query.query}\n\nAvailable Businesses:\n{businesses_info}"}
            ],
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        matching_businesses = [
            business for business in query.businesses 
            if business['id'] in result.get('matching_ids', [])
        ]
        
        return {
            "keywords": result.get('keywords', []),
            "matches": matching_businesses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}