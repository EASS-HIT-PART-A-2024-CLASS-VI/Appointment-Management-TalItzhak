from datetime import datetime, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, validator , Field
from enum import Enum

class DayOfWeek(str, Enum):
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name: str
    last_name: str
    username: str
    phone: str
    business_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: str  # Either "business_owner" or "customer"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    username: str
    phone: str
    role: str
    business_name: Optional[str] = None

# Service Schemas
class ServiceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    duration: int  # Duration of the service in minutes
    price: int 

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[int] = None

class ServiceResponse(ServiceBase):
    id: int
    owner_id: int
    topics: List["TopicResponse"] = []  

class TopicBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    duration: int
    cost: int

class TopicCreate(TopicBase):
    service_id: int 

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    cost: Optional[int] = None

class TopicResponse(TopicBase):
    id: int

class AppointmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: datetime
    start_time: time  # Format as HH:MM
    duration: int  # Duration in minutes
    title: str
    customer_name: str
    customer_phone: str
    type: str
    cost: int
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    date: datetime
    start_time: time
    title: str  
    customer_name: str
    customer_phone: str

class AppointmentUpdate(BaseModel):
    date: Optional[datetime] = None
    start_time: Optional[time] = None
    title: Optional[str] = None  
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None  

class AppointmentResponse(AppointmentBase):
    id: int

class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    username: str
    services: List[ServiceResponse]
    business_name: Optional[str]  


class AvailabilityBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    day_of_week: DayOfWeek  
    start_time: time
    end_time: time

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityResponse(AvailabilityBase):
    id: int
    owner_id: int

class BusinessAvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    business_id: int
    business_name: str
    availability: List[AvailabilityResponse]

class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total: int
    items: List[BaseModel]

TopicResponse.model_rebuild()
ServiceResponse.model_rebuild()

class SearchQuery(BaseModel):
    query: str



class MessageTitle(str, Enum):
    RESCHEDULE = "Rescheduling an Appointment"
    CANCEL = "Canceling an Appointment"
    QUESTIONS = "Questions About Services"
    PAYMENT = "Payment and Billing Issues"
    OTHER = "Other Inquiries"

class MessageCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: MessageTitle
    content: str = Field(..., min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    created_at: datetime
    read: bool
    sender_name: str 
    recipient_name: str