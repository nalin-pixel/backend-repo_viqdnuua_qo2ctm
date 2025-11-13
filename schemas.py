"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    room_type: Optional[str] = Field(None, description="Room type like living room, bedroom")
    image_url: Optional[HttpUrl] = Field(None, description="Primary product image URL (WebP preferred)")
    in_stock: bool = Field(True, description="Whether product is in stock")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for filtering/search")

class Testimonial(BaseModel):
    """
    Customer testimonials
    Collection name: "testimonial"
    """
    client_name: str = Field(..., description="Client name")
    project_type: Optional[str] = Field(None, description="Project type e.g., Full Home, Kitchen")
    rating: int = Field(5, ge=1, le=5, description="Rating out of 5")
    quote: str = Field(..., description="Client quote")
    photo_url: Optional[HttpUrl] = Field(None, description="Client or project photo URL")
    case_study_url: Optional[HttpUrl] = Field(None, description="Link to full case study")

class Project(BaseModel):
    """
    Portfolio projects
    Collection name: "project"
    """
    title: str = Field(...)
    style: Optional[str] = Field(None, description="Modern, Traditional, Minimalist, etc.")
    room: Optional[str] = Field(None, description="Living Room, Bedroom, etc.")
    budget_range: Optional[str] = Field(None)
    duration_weeks: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None)
    before_image_url: Optional[HttpUrl] = Field(None)
    after_image_url: Optional[HttpUrl] = Field(None)
    gallery: Optional[List[HttpUrl]] = Field(default_factory=list)

class Lead(BaseModel):
    """
    Sales leads from contact/consultation forms
    Collection name: "lead"
    """
    name: str = Field(...)
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(None)
    project_details: Optional[str] = Field(None)
    preferred_date: Optional[datetime] = Field(None)
    source: Optional[str] = Field("website", description="lead source")
    consent: bool = Field(True, description="User consent for contact/marketing")

class BlogPost(BaseModel):
    """
    Blog posts for SEO content
    Collection name: "blogpost"
    """
    title: str = Field(...)
    slug: str = Field(...)
    excerpt: Optional[str] = Field(None)
    content: str = Field(...)
    cover_image_url: Optional[HttpUrl] = Field(None)
    keywords: Optional[List[str]] = Field(default_factory=list)
    published: bool = Field(True)
