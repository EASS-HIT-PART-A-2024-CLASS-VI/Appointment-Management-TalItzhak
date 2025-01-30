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

def extract_keywords(query: str) -> List[str]:
    """Extract meaningful keywords from the search query"""
    # Common words to ignore
    stop_words = {
        'i', 'need', 'want', 'looking', 'for', 'a', 'the', 'to', 'in', 'on', 'at',
        'who', 'what', 'where', 'when', 'how', 'can', 'could', 'would', 'should',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'and', 'or', 'but', 'if', 'then', 'else', 'my', 'your',
        'please', 'thanks', 'help', 'with', 'any', 'some', 'someone'
    }
    
    # Split query into words and filter out stop words
    words = query.lower().replace('?', '').replace('!', '').replace('.', '').split()
    keywords = [word for word in words if word not in stop_words]
    
    return list(set(keywords))  # Remove duplicates

def calculate_relevance_score(business: dict, keywords: List[str]) -> float:
    """Calculate how relevant a business is to the search keywords"""
    score = 0
    business_name = business['business_name'].lower()
    
    # Check business name
    for keyword in keywords:
        if keyword in business_name:
            score += 2  # Business name matches are weighted more heavily
    
    # Check services
    for service in business['services']:
        service_name = service['name'].lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in service_name)
        if keyword_matches > 0:
            score += 3 * keyword_matches  # Service matches are weighted most heavily
    
    return score

@app.post("/analyze-query")
async def analyze_query(query: SearchQuery):
    try:
        print(f"Received query: {query.query}")
        
        # Extract meaningful keywords
        keywords = extract_keywords(query.query)
        print(f"Extracted keywords: {keywords}")
        
        # Calculate relevance scores for each business
        scored_businesses = []
        for business in query.businesses:
            score = calculate_relevance_score(business, keywords)
            if score > 0:  # Only include businesses with positive relevance
                scored_businesses.append((score, business))
        
        # Sort by score and take top matches
        scored_businesses.sort(reverse=True, key=lambda x: x[0])
        
        # Only return businesses with significant relevance
        relevant_businesses = [business for score, business in scored_businesses if score >= 3]
        
        print(f"Found {len(relevant_businesses)} relevant businesses")
        return {
            "matches": relevant_businesses
        }

    except Exception as e:
        print(f"Error in analyze_query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "keyword-matching"}