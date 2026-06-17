import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


# -------------------- Basic settings --------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-real-projects")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jwt_auth.db")
FRONTEND_FOLDER = Path(__file__).parent / "frontend"


# -------------------- Database setup --------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Database tables --------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class RentalRecord(Base):
    __tablename__ = "rental_records"

    id = Column(Integer, primary_key=True, index=True)
    property_name = Column(String, nullable=False)
    property_address = Column(String, nullable=False)
    tenant_name = Column(String, nullable=False)
    tenant_phone = Column(String, nullable=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    monthly_rent = Column(Integer, nullable=False)
    payment_status = Column(String, default="Pending")
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)


Base.metadata.create_all(bind=engine)


# -------------------- Request and response models --------------------

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    is_active: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RentalCreate(BaseModel):
    property_name: str
    property_address: str
    tenant_name: str
    tenant_phone: str | None = None
    start_date: str
    end_date: str
    monthly_rent: int
    payment_status: str = "Pending"
    notes: str | None = None


class RentalUpdate(BaseModel):
    property_name: str
    property_address: str
    tenant_name: str
    tenant_phone: str | None = None
    start_date: str
    end_date: str
    monthly_rent: int
    payment_status: str
    notes: str | None = None


class RentalResponse(BaseModel):
    id: int
    property_name: str
    property_address: str
    tenant_name: str
    tenant_phone: str | None = None
    start_date: str
    end_date: str
    monthly_rent: int
    payment_status: str
    notes: str | None = None

    class Config:
        orm_mode = True


# -------------------- Password and JWT helpers --------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str):
    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(username: str):
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    data = {
        "sub": username,
        "exp": expire_time,
    }

    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_demo_user():
    db = SessionLocal()
    try:
        demo_user = get_user_by_username(db, "manager")
        if demo_user is None:
            demo_user = User(
                username="manager",
                full_name="Property Manager",
                hashed_password=hash_password("secret123"),
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


create_demo_user()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_username(db, username)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# -------------------- FastAPI app and routes --------------------

app = FastAPI(title="Property Rental Management JWT Project")

app.mount("/frontend", StaticFiles(directory=FRONTEND_FOLDER), name="frontend")


@app.get("/")
def home():
    return {
        "message": "Property Rental Management project is running",
        "frontend": "Open /app to use the frontend",
        "docs": "Open /docs to test the API",
    }


@app.get("/app")
def frontend_app():
    return FileResponse(FRONTEND_FOLDER / "index.html")


@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    old_user = get_user_by_username(db, user_data.username)

    if old_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Account not found. Create an account first or use the demo login.",
        )

    password_is_correct = verify_password(
        form_data.password,
        user.hashed_password,
    )

    if not password_is_correct:
        raise HTTPException(status_code=401, detail="Password is incorrect")

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/me", response_model=UserResponse)
def read_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "You can see this because your JWT token is valid",
        "username": current_user.username,
    }


@app.get("/rentals", response_model=list[RentalResponse])
def get_my_rentals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rentals = db.query(RentalRecord).filter(RentalRecord.owner_id == current_user.id).all()
    return rentals


@app.post("/rentals", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def add_rental(
    rental_data: RentalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if rental_data.monthly_rent <= 0:
        raise HTTPException(status_code=400, detail="Monthly rent must be greater than 0")

    new_rental = RentalRecord(
        property_name=rental_data.property_name,
        property_address=rental_data.property_address,
        tenant_name=rental_data.tenant_name,
        tenant_phone=rental_data.tenant_phone,
        start_date=rental_data.start_date,
        end_date=rental_data.end_date,
        monthly_rent=rental_data.monthly_rent,
        payment_status=rental_data.payment_status,
        notes=rental_data.notes,
        owner_id=current_user.id,
    )

    db.add(new_rental)
    db.commit()
    db.refresh(new_rental)

    return new_rental


@app.put("/rentals/{rental_id}", response_model=RentalResponse)
def update_rental(
    rental_id: int,
    rental_data: RentalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rental = (
        db.query(RentalRecord)
        .filter(RentalRecord.id == rental_id, RentalRecord.owner_id == current_user.id)
        .first()
    )

    if rental is None:
        raise HTTPException(status_code=404, detail="Rental record not found")

    if rental_data.monthly_rent <= 0:
        raise HTTPException(status_code=400, detail="Monthly rent must be greater than 0")

    rental.property_name = rental_data.property_name
    rental.property_address = rental_data.property_address
    rental.tenant_name = rental_data.tenant_name
    rental.tenant_phone = rental_data.tenant_phone
    rental.start_date = rental_data.start_date
    rental.end_date = rental_data.end_date
    rental.monthly_rent = rental_data.monthly_rent
    rental.payment_status = rental_data.payment_status
    rental.notes = rental_data.notes

    db.commit()
    db.refresh(rental)

    return rental


@app.delete("/rentals/{rental_id}")
def delete_rental(
    rental_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rental = (
        db.query(RentalRecord)
        .filter(RentalRecord.id == rental_id, RentalRecord.owner_id == current_user.id)
        .first()
    )

    if rental is None:
        raise HTTPException(status_code=404, detail="Rental record not found")

    db.delete(rental)
    db.commit()

    return {"message": "Rental record deleted"}
