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
# Business owner endpoints
@router.post("/services", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """Create a new service (only for business owners)"""
    # Get the user first
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Debug print
    print(f"Creating service for user ID: {user.id}")

    new_service = Service(
        name=service.name,
        duration=service.duration,
        price=service.price,
        owner_id=user.id  # Use the actual user ID
    )
    
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    
    # Debug print
    print(f"Created service: {new_service.id} for owner: {new_service.owner_id}")
    
    return new_service


@router.get("/my-services", response_model=List[ServiceResponse])
def get_my_services(
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """Get all services for the logged-in business owner"""
    # First, get the user from the database using the username from the token
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get services using the actual user ID
    services = db.query(Service).filter(Service.owner_id == user.id).all()
    
    # Add debug printing
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
    # Get the user first
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find the service and verify ownership using the actual user ID
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == user.id  # Updated to use the actual user ID
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found or you don't have permission to modify it"
        )
    
    # Rest of the code remains the same
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
    # Get the user first
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.owner_id == user.id  # Updated to use the actual user ID
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found or you don't have permission to delete it"
        )
    
    # First delete all associated topics
    for topic in service.topics:
        db.delete(topic)
    
    # Then delete the service
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
        
        # Check business name match
        for term in query_terms:
            if term in business_text:
                score += 1
        
        # Check services match
        for service in business.services:
            service_text = service.name.lower()
            for term in query_terms:
                if term in service_text:
                    score += 2  # Services matches are weighted higher
        
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
    
    # Sort by relevance score
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
    Search for businesses and services based on query text
    """
    try:
        # Get all businesses with their services
        businesses = db.query(User).filter(
            User.role == "business_owner"
        ).all()
        
        # Perform search
        matches = search_businesses(query.query, businesses)
        
        return {"matches": matches}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}"
        )