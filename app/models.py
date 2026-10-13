import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class BillingCycle(str, enum.Enum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"


class Category(str, enum.Enum):
    ENTERTAINMENT = "Entertainment"
    INFRASTRUCTURE = "Infrastructure"
    FITNESS = "Fitness"
    SOFTWARE = "Software"
    UTILITIES = "Utilities"
    OTHER = "Other"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "Active"
    CANCELLED = "Cancelled"
    TRIAL = "Trial"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # One-to-Many relationship with Subscriptions
    subscriptions = relationship("Subscriptions", back_populates="owner", cascade="all, delete-orphan")


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY, nullable=False)
    next_billing_date = Column(Date, nullable=False)
    category = Column(Enum(Category), default=Category.OTHER, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to User
    owner = relationship("Users", back_populates="subscriptions")