"""
BorrowBox - Backend
-------------------
A simple, single-file FastAPI backend for a rent/buy marketplace.

Stack: FastAPI + MongoDB (PyMongo) + Cloudinary + JWT auth.

Run locally:
    uvicorn main:app --reload

Everything lives in this one file on purpose - this is a college MVP,
not a production microservice system. Keep it simple.
"""

import os
import re
import math
from datetime import datetime, timedelta, date
from typing import Optional, List

import certifi
import cloudinary
import cloudinary.uploader
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from pymongo import MongoClient

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["BorrowBox"]

users_col = db["users"]
products_col = db["products"]
transactions_col = db["transactions"]
categories_col = db["categories"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(title="BorrowBox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # college MVP - keep CORS open
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_CATEGORIES = [
    "Property", "Furniture", "Electronics", "Vehicles", "Gaming",
    "Cameras", "Appliances", "Tools", "Sports", "Study", "Other",
]

VALID_ROLES = {"customer", "seller"}
VALID_RENT_PERIODS = {"day", "week", "month"}
VALID_TXN_STATUSES = {"pending", "approved", "completed", "cancelled"}

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def oid(id_str: str) -> ObjectId:
    """Convert a string to a MongoDB ObjectId, raising a clean 400 on failure."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail="Invalid id format")


def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "phone": user.get("phone"),
    }


def serialize_product(product: dict) -> dict:
    return {
        "id": str(product["_id"]),
        "seller_id": str(product["seller_id"]),
        "title": product["title"],
        "description": product["description"],
        "category": product["category"],
        "location": product["location"],
        "buy_price": product.get("buy_price"),
        "rent_price": product.get("rent_price"),
        "rent_period": product.get("rent_period"),
        "image_urls": product.get("image_urls", []),
        "available_for_sale": product.get("available_for_sale", False),
        "available_for_rent": product.get("available_for_rent", False),
        "status": product.get("status", "active"),
        "created_at": product.get("created_at"),
    }


def serialize_transaction(txn: dict) -> dict:
    return {
        "id": str(txn["_id"]),
        "product_id": str(txn["product_id"]),
        "customer_id": str(txn["customer_id"]),
        "seller_id": str(txn["seller_id"]),
        "type": txn["type"],
        "amount": txn["amount"],
        "status": txn["status"],
        "start_date": txn.get("start_date"),
        "end_date": txn.get("end_date"),
        "created_at": txn.get("created_at"),
    }


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Extract and verify the JWT, then load the current user from MongoDB."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = users_col.find_one({"_id": oid(user_id)})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_seller(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Sellers only")
    return user


def require_customer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Customers only")
    return user


def calculate_rent_amount(rent_price: float, rent_period: str, start: date, end: date) -> float:
    """Simple duration-based rent calculation. No availability calendars."""
    days = (end - start).days
    if days <= 0:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")

    if rent_period == "day":
        units = days
    elif rent_period == "week":
        units = math.ceil(days / 7)
    elif rent_period == "month":
        units = math.ceil(days / 30)
    else:
        raise HTTPException(status_code=400, detail="Invalid rent period")

    return round(rent_price * units, 2)


# ------------------------------------------------------------------
# Pydantic schemas
# ------------------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str
    phone: str = Field(min_length=6, max_length=20)

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v):
        if v not in VALID_ROLES:
            raise ValueError("role must be 'customer' or 'seller'")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProductCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=3000)
    category: str
    location: str = Field(min_length=1, max_length=150)
    buy_price: Optional[float] = None
    rent_price: Optional[float] = None
    rent_period: Optional[str] = None
    image_urls: List[str] = Field(min_length=1)
    available_for_sale: bool = False
    available_for_rent: bool = False

    @field_validator("buy_price", "rent_price")
    @classmethod
    def price_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("price cannot be negative")
        return v

    @field_validator("rent_period")
    @classmethod
    def rent_period_valid(cls, v):
        if v is not None and v not in VALID_RENT_PERIODS:
            raise ValueError("rent_period must be day, week, or month")
        return v


class ProductUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    buy_price: Optional[float] = None
    rent_price: Optional[float] = None
    rent_period: Optional[str] = None
    image_urls: Optional[List[str]] = None
    available_for_sale: Optional[bool] = None
    available_for_rent: Optional[bool] = None


class BuyRequest(BaseModel):
    product_id: str


class RentRequest(BaseModel):
    product_id: str
    start_date: date
    end_date: date


class TransactionStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v):
        if v not in VALID_TXN_STATUSES:
            raise ValueError(f"status must be one of {VALID_TXN_STATUSES}")
        return v


# ------------------------------------------------------------------
# Startup - seed categories
# ------------------------------------------------------------------

@app.on_event("startup")
def seed_categories():
    if categories_col.count_documents({}) == 0:
        categories_col.insert_many([{"name": c} for c in DEFAULT_CATEGORIES])


# ------------------------------------------------------------------
# Auth endpoints
# ------------------------------------------------------------------

@app.post("/api/auth/register")
def register(payload: RegisterRequest):
    if users_col.find_one({"email": payload.email.lower()}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(payload.password)
    user_doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "password": hashed_password,
        "role": payload.role,
        "phone": payload.phone,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = users_col.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    return {
        "success": True,
        "message": "Registration successful",
        "user": serialize_user(user_doc),
    }


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = users_col.find_one({"email": payload.email.lower()})
    if not user or not pwd_context.verify(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(user["_id"]))

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }


@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return serialize_user(current_user)


# ------------------------------------------------------------------
# Categories
# ------------------------------------------------------------------

@app.get("/api/categories")
def get_categories():
    cats = list(categories_col.find({}))
    return {"categories": [c["name"] for c in cats]}


# ------------------------------------------------------------------
# Image upload
# ------------------------------------------------------------------

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@app.post("/api/upload")
def upload_image(file: UploadFile = File(...), current_user: dict = Depends(require_seller)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, webp images are allowed")

    result = cloudinary.uploader.upload(
        file.file,
        folder="BorrowBox",
        resource_type="image",
    )

    return {"success": True, "url": result["secure_url"]}


# ------------------------------------------------------------------
# Products
# ------------------------------------------------------------------

@app.post("/api/products")
def create_product(payload: ProductCreateRequest, current_user: dict = Depends(require_seller)):
    if not payload.available_for_sale and not payload.available_for_rent:
        raise HTTPException(
            status_code=400,
            detail="Listing must be available for sale, rent, or both",
        )

    if payload.available_for_sale and payload.buy_price is None:
        raise HTTPException(status_code=400, detail="buy_price is required when available for sale")

    if payload.available_for_rent and (payload.rent_price is None or payload.rent_period is None):
        raise HTTPException(
            status_code=400,
            detail="rent_price and rent_period are required when available for rent",
        )

    product_doc = {
        "seller_id": current_user["_id"],
        "title": payload.title,
        "description": payload.description,
        "category": payload.category,
        "location": payload.location,
        "buy_price": payload.buy_price,
        "rent_price": payload.rent_price,
        "rent_period": payload.rent_period,
        "image_urls": payload.image_urls,
        "available_for_sale": payload.available_for_sale,
        "available_for_rent": payload.available_for_rent,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }
    result = products_col.insert_one(product_doc)
    product_doc["_id"] = result.inserted_id

    return {"success": True, "product": serialize_product(product_doc)}


@app.get("/api/products")
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    available_for_sale: Optional[bool] = Query(None),
    available_for_rent: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = {"status": "active"}

    if search:
        query["$or"] = [
            {"title": {"$regex": re.escape(search), "$options": "i"}},
            {"description": {"$regex": re.escape(search), "$options": "i"}},
        ]
    if category:
        query["category"] = category
    if location:
        query["location"] = {"$regex": re.escape(location), "$options": "i"}
    if available_for_sale is not None:
        query["available_for_sale"] = available_for_sale
    if available_for_rent is not None:
        query["available_for_rent"] = available_for_rent

    skip = (page - 1) * limit
    cursor = products_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    products = [serialize_product(p) for p in cursor]
    total = products_col.count_documents(query)

    return {"products": products, "total": total, "page": page, "limit": limit}


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    product = products_col.find_one({"_id": oid(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = serialize_product(product)

    seller = users_col.find_one({"_id": product["seller_id"]})
    if seller:
        result["seller"] = {
            "id": str(seller["_id"]),
            "name": seller["name"],
            "phone": seller.get("phone"),
        }

    return result


@app.put("/api/products/{product_id}")
def update_product(product_id: str, payload: ProductUpdateRequest, current_user: dict = Depends(require_seller)):
    product = products_col.find_one({"_id": oid(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="You do not own this listing")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if update_data:
        for price_field in ("buy_price", "rent_price"):
            if price_field in update_data and update_data[price_field] < 0:
                raise HTTPException(status_code=400, detail=f"{price_field} cannot be negative")
        products_col.update_one({"_id": product["_id"]}, {"$set": update_data})

    updated = products_col.find_one({"_id": product["_id"]})
    return {"success": True, "product": serialize_product(updated)}


@app.delete("/api/products/{product_id}")
def deactivate_product(product_id: str, current_user: dict = Depends(require_seller)):
    product = products_col.find_one({"_id": oid(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="You do not own this listing")

    products_col.update_one({"_id": product["_id"]}, {"$set": {"status": "inactive"}})
    return {"success": True, "message": "Listing deactivated"}


# ------------------------------------------------------------------
# Seller-specific views
# ------------------------------------------------------------------

@app.get("/api/seller/products")
def seller_products(current_user: dict = Depends(require_seller)):
    cursor = products_col.find({"seller_id": current_user["_id"]}).sort("created_at", -1)
    return {"products": [serialize_product(p) for p in cursor]}


@app.get("/api/seller/transactions")
def seller_transactions(current_user: dict = Depends(require_seller)):
    cursor = transactions_col.find({"seller_id": current_user["_id"]}).sort("created_at", -1)
    return {"transactions": [serialize_transaction(t) for t in cursor]}


# ------------------------------------------------------------------
# Transactions - buy / rent
# ------------------------------------------------------------------

@app.post("/api/transactions/buy")
def buy_product(payload: BuyRequest, current_user: dict = Depends(require_customer)):
    product = products_col.find_one({"_id": oid(payload.product_id)})
    if not product or product.get("status") != "active":
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.get("available_for_sale"):
        raise HTTPException(status_code=400, detail="This product is not available for sale")

    amount = product["buy_price"]  # price always comes from DB, never from client

    txn_doc = {
        "product_id": product["_id"],
        "customer_id": current_user["_id"],
        "seller_id": product["seller_id"],
        "type": "buy",
        "amount": amount,
        "status": "pending",
        "start_date": None,
        "end_date": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    result = transactions_col.insert_one(txn_doc)
    txn_doc["_id"] = result.inserted_id

    return {"success": True, "transaction": serialize_transaction(txn_doc)}


@app.post("/api/transactions/rent")
def rent_product(payload: RentRequest, current_user: dict = Depends(require_customer)):
    product = products_col.find_one({"_id": oid(payload.product_id)})
    if not product or product.get("status") != "active":
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.get("available_for_rent"):
        raise HTTPException(status_code=400, detail="This product is not available for rent")

    amount = calculate_rent_amount(
        rent_price=product["rent_price"],
        rent_period=product["rent_period"],
        start=payload.start_date,
        end=payload.end_date,
    )

    txn_doc = {
        "product_id": product["_id"],
        "customer_id": current_user["_id"],
        "seller_id": product["seller_id"],
        "type": "rent",
        "amount": amount,
        "status": "pending",
        "start_date": payload.start_date.isoformat(),
        "end_date": payload.end_date.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    result = transactions_col.insert_one(txn_doc)
    txn_doc["_id"] = result.inserted_id

    return {"success": True, "transaction": serialize_transaction(txn_doc)}


@app.get("/api/transactions/my")
def my_transactions(current_user: dict = Depends(require_customer)):
    cursor = transactions_col.find({"customer_id": current_user["_id"]}).sort("created_at", -1)
    return {"transactions": [serialize_transaction(t) for t in cursor]}


@app.put("/api/transactions/{transaction_id}/status")
def update_transaction_status(
    transaction_id: str,
    payload: TransactionStatusUpdate,
    current_user: dict = Depends(require_seller),
):
    txn = transactions_col.find_one({"_id": oid(transaction_id)})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="You do not own this transaction")

    transactions_col.update_one({"_id": txn["_id"]}, {"$set": {"status": payload.status}})
    updated = transactions_col.find_one({"_id": txn["_id"]})
    return {"success": True, "transaction": serialize_transaction(updated)}


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "service": "BorrowBox API"}