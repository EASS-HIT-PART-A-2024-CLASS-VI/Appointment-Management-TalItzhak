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



# routes/services.py


@router.post("/smart-service-search", response_model=List[BusinessResponse])
async def smart_service_search(
    search_query: SearchQuery,
    db: Session = Depends(get_db)
):
    try:
        # Normalize search query
        search_text = search_query.query.lower()
        
        # Extract keywords from search query
        keywords = re.findall(r'\w+', search_text)
        
        if not keywords:
            raise HTTPException(status_code=400, detail="Search query is required")

        # Create filters for each keyword
        service_filters = []
        business_filters = []
        
        # Common word substitutions
        word_substitutions = {
            'fix': ['repair', 'restore', 'mend', 'service'],
            'repair': ['fix', 'restore', 'mend', 'service'],
            'screen': ['display', 'monitor', 'lcd'],
            'phone': ['mobile', 'smartphone', 'device', 'cellular'],
        }

        # Add filters for original keywords and their substitutions
        for keyword in keywords:
            # Add original keyword
            service_filters.append(Service.name.ilike(f'%{keyword}%'))
            business_filters.append(User.business_name.ilike(f'%{keyword}%'))

            # Add substitutions if they exist
            if keyword in word_substitutions:
                for substitute in word_substitutions[keyword]:
                    service_filters.append(Service.name.ilike(f'%{substitute}%'))

        # Query for businesses that match any of the filters
        businesses = db.query(User).filter(
            User.role == "business_owner"
        ).filter(
            or_(
                # Match business name
                or_(*business_filters),
                # Match service name
                User.services.any(or_(*service_filters))
            )
        ).all()

        # Sort businesses by relevance
        def calculate_relevance(business):
            relevance_score = 0
            
            # Check business name
            if any(keyword in business.business_name.lower() for keyword in keywords):
                relevance_score += 10
                
            # Check services
            for service in business.services:
                service_name = service.name.lower()
                # Direct keyword matches
                for keyword in keywords:
                    if keyword in service_name:
                        relevance_score += 5
                    # Substitution matches
                    if keyword in word_substitutions:
                        for substitute in word_substitutions[keyword]:
                            if substitute in service_name:
                                relevance_score += 3
                
                # Exact phrase match gives bonus points
                if search_text in service_name:
                    relevance_score += 15
                    
            return relevance_score

        # Sort businesses by relevance score
        sorted_businesses = sorted(
            businesses,
            key=calculate_relevance,
            reverse=True
        )

        # Filter out businesses with zero relevance
        relevant_businesses = [b for b in sorted_businesses if calculate_relevance(b) > 0]

        return relevant_businesses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))