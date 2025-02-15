from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, business_owner_required
from app.models import Message, User
from app.schemas import MessageCreate, MessageResponse
from datetime import datetime
from typing import List
from sqlalchemy import desc
import pytz


router = APIRouter()

@router.post("/send/{business_id}", response_model=MessageResponse)
async def send_message_to_business(
    business_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send a message to a specific business owner"""
    try:
        print(f"Looking for sender with username: {current_user['sub']}")
        sender = db.query(User).filter(User.username == current_user["sub"]).first()
        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")
        
        print(f"Sender found: {sender.first_name} {sender.last_name}, role: {sender.role}")
        if sender.role != "customer":
            raise HTTPException(status_code=403, detail="Only customers can send messages to businesses")
        
        print(f"Looking for business owner with ID: {business_id}")
        recipient = db.query(User).filter(
            User.id == business_id,
            User.role == "business_owner"
        ).first()
        
        if not recipient:
            raise HTTPException(
                status_code=404, 
                detail=f"Business owner with ID {business_id} not found"
            )
        
        print(f"Recipient found: {recipient.first_name} {recipient.last_name}")
        
        # Create new message with Israel timezone
        israel_tz = pytz.timezone('Asia/Jerusalem')
        current_time = datetime.now() 
        
        print(f"Creating message with title: {message.title}")
        db_message = Message(
            sender_id=sender.id,
            recipient_id=recipient.id,
            title=message.title.value,
            content=message.content,
            created_at=current_time,
            read=False
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        response = MessageResponse(
            id=db_message.id,
            title=db_message.title,
            content=db_message.content,
            created_at=db_message.created_at,
            read=db_message.read,
            sender_name=f"{sender.first_name} {sender.last_name}",
            recipient_name=f"{recipient.first_name} {recipient.last_name}"
        )
        
        print(f"Message created successfully: {response}")
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error creating message: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/my-messages", response_model=List[MessageResponse])
async def get_my_messages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for the current business owner"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "business_owner":
        raise HTTPException(status_code=403, detail="Only business owners can view their messages")
    
    # Get all messages sent to this business owner
    messages = db.query(Message).filter(
        Message.recipient_id == user.id
    ).order_by(desc(Message.created_at)).all()
    
    # Add sender names to response
    response_messages = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        
        # Create MessageResponse object with all required fields
        message_response = MessageResponse(
            id=msg.id,
            title=msg.title,
            content=msg.content,
            created_at=msg.created_at,
            read=msg.read,
            sender_name=f"{sender.first_name} {sender.last_name}",
            recipient_name=f"{user.first_name} {user.last_name}"
        )
        response_messages.append(message_response)
    
    return response_messages

@router.patch("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark a message as read"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "business_owner":
        raise HTTPException(status_code=403, detail="Only business owners can mark messages as read")
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found or you don't have permission to mark it as read"
        )
    
    message.read = True
    db.commit()
    
    return {"message": "Message marked as read"}

@router.get("/unread-count")
async def get_unread_messages_count(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get count of unread messages for business owner"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user or user.role != "business_owner":
        return {"unread_count": 0}
    
    count = db.query(Message).filter(
        Message.recipient_id == user.id,
        Message.read == False
    ).count()
    
    return {"unread_count": count}



@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(business_owner_required)
):
    """Delete a message (business owners only)"""
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found or you don't have permission to delete it"
        )
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully"}