from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import re
from typing import List
from app.models import Topic, Service
from app.models import Availability
from openai import OpenAI
from app.schemas import (
    TopicCreate, 
    TopicUpdate, 
    TopicResponse, 
    ServiceCreate, 
    ServiceUpdate, 
    ServiceResponse,
    BusinessResponse,
    SearchQuery
)
from app.dependencies import get_db, business_owner_required, get_current_user
from app.models import User
from app.models import Service
from sqlalchemy import or_
import httpx
import json 


router = APIRouter()

@router.get("/public/businesses", response_model=List[BusinessResponse])
def get_all_businesses(db: Session = Depends(get_db)):
    """Get all users who are business owners with their services"""
    businesses = db.query(User).filter(User.role == "business_owner").all()
    return businesses

@router.get("/public/businesses/{business_id}/services", response_model=List[ServiceResponse])
def get_business_services(business_id: int, db: Session = Depends(get_db)):
    """Get all services for a specific business"""
    services = db.query(Service).filter(Service.owner_id == business_id).all()
    if not services:
        raise HTTPException(status_code=404, detail="No services found for this business")
    return services


@router.get("/public/businesses/{business_id}/availability")
def get_business_availability(business_id: int, db: Session = Depends(get_db)):
    """Get the business's availability schedule"""
    availability = db.query(Availability)\
        .filter(Availability.owner_id == business_id)\
        .all()
    
    if not availability:
        raise HTTPException(status_code=404, detail="No availability found for this business")
    
    return availability

# Create a topic
@router.post("/services", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """Create a new service (only for business owners)"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    print(f"Creating service for user ID: {user.id}")

    new_service = Service(
        name=service.name,
        duration=service.duration,
        price=service.price,
        owner_id=user.id  
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    print(f"Created service: {new_service.id} for owner: {new_service.owner_id}")
    
    return new_service


@router.get("/my-services", response_model=List[ServiceResponse])
def get_my_services(
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """Get all services for the logged-in business owner"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    services = db.query(Service).filter(Service.owner_id == user.id).all()
    
    print(f"Looking for services for user ID: {user.id}")
    print(f"Found services: {services}")
    
    return services

# Update a topic
@router.put("/services/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == user.id  
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found or you don't have permission to modify it"
        )
    
    if service_update.name is not None:
        service.name = service_update.name
    if service_update.duration is not None:
        service.duration = service_update.duration
    if service_update.price is not None:
        service.price = service_update.price
    
    db.commit()
    db.refresh(service)
    return service


@router.delete("/services/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == user.id 
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found or you don't have permission to delete it"
        )
    
    for topic in service.topics:
        db.delete(topic)
    
    db.delete(service)
    db.commit()
    
    return {"message": f"Service '{service.name}' and all its topics have been deleted successfully"}

def search_businesses(query: str, businesses_data: list) -> list:
    """
    Search for businesses based on query text.
    Returns list of relevant businesses with their services.
    """
    query_terms = query.lower().split()
    matching_businesses = []
    
    for business in businesses_data:
        score = 0
        business_text = (
            f"{business.business_name or ''} "
            f"{business.first_name or ''} "
            f"{business.last_name or ''}"
        ).lower()
        
        for term in query_terms:
            if term in business_text:
                score += 1
        
        for service in business.services:
            service_text = service.name.lower()
            for term in query_terms:
                if term in service_text:
                    score += 2  
        
        if score > 0:
            matching_businesses.append({
                "id": business.id,
                "business_name": business.business_name,
                "first_name": business.first_name,
                "last_name": business.last_name,
                "services": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "duration": s.duration,
                        "price": s.price
                    } for s in business.services
                ],
                "score": score
            })
    
    return sorted(matching_businesses, key=lambda x: x["score"], reverse=True)

@router.get("/public/businesses", response_model=List[BusinessResponse])
def get_all_businesses(db: Session = Depends(get_db)):
    """Get all users who are business owners with their services"""
    businesses = db.query(User).filter(User.role == "business_owner").all()
    return businesses

@router.get("/public/businesses/{business_id}/services", response_model=List[ServiceResponse])
def get_business_services(business_id: int, db: Session = Depends(get_db)):
    """Get all services for a specific business"""
    services = db.query(Service).filter(Service.owner_id == business_id).all()
    if not services:
        raise HTTPException(status_code=404, detail="No services found for this business")
    return services

@router.post("/smart-service-search")
async def smart_service_search(query: SearchQuery, db: Session = Depends(get_db)):
    """
    Search for businesses and services using LLM service
    """
    try:
        businesses = db.query(User).filter(
            User.role == "business_owner"
        ).all()
        
        businesses_data = [{
            "id": business.id,
            "business_name": business.business_name or f"{business.first_name} {business.last_name}",
            "first_name": business.first_name,
            "last_name": business.last_name,
            "services": [{
                "id": service.id,
                "name": service.name,
                "duration": service.duration,
                "price": service.price
            } for service in business.services]
        } for business in businesses]

        llm_url = "http://llm_service:8001/analyze-query"
        print(f"Connecting to LLM service at: {llm_url}")
        
        async with httpx.AsyncClient() as client:
            try:
                # Send request to LLM service
                llm_response = await client.post(
                    llm_url,
                    json={
                        "query": query.query,
                        "businesses": businesses_data
                    },
                    timeout=30.0  
                )
                
                if llm_response.status_code == 200:
                    llm_data = llm_response.json()
                    print(f"LLM service response: {llm_data}")
                    
                    if "matches" in llm_data:
                        return {
                            "matches": llm_data["matches"]
                        }
                    else:
                        return {"matches": []}
                else:
                    print(f"LLM service error: {llm_response.text}")
                    raise HTTPException(
                        status_code=llm_response.status_code,
                        detail=f"LLM service error: {llm_response.text}"
                    )
                    
            except httpx.RequestError as e:
                print(f"Connection error to LLM service: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Error connecting to LLM service: {str(e)}"
                )
            
    except Exception as e:
        print(f"Unexpected error in smart_service_search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )