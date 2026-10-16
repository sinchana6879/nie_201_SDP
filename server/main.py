
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session,
)

from config import DATABASE_URL, FRONTEND_URL


# Database configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Database model
class Base(DeclarativeBase):
    pass


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    student_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    event_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


# Create the database table when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="College Event Registration API",
    description="API for registering students for college events",
    version="1.0.0",
    lifespan=lifespan,
)


# Allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Request schema
# Accepts studentName, email, and eventName from the frontend.
class EventRegistrationSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    student_name: str = Field(
        alias="studentName",
        min_length=1,
        max_length=100
    )

    email: str = Field(
        min_length=1,
        max_length=150
    )

    event_name: str = Field(
        alias="eventName",
        min_length=1,
        max_length=100
    )


# Response schema
class EventRegistrationResponse(EventRegistrationSchema):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


# GET /events
# Retrieve all event registrations.
@app.get(
    "/events",
    response_model=list[EventRegistrationResponse]
)
def get_events(db: Session = Depends(get_db)):
    return (
        db.query(EventRegistration)
        .order_by(EventRegistration.id)
        .all()
    )


# POST /events
# Register a student for an event.
@app.post(
    "/events",
    response_model=EventRegistrationResponse,
    status_code=201
)
def register_event(
    registration: EventRegistrationSchema,
    db: Session = Depends(get_db)
):
    new_registration = EventRegistration(
        student_name=registration.student_name.strip(),
        email=registration.email.strip(),
        event_name=registration.event_name.strip()
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration
