from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, computed_field

from app.models import BillingCycle, Category, SubscriptionStatus


# ==========================================
# 1. USER SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    currency: Optional[str] = Field(default="INR", min_length=3, max_length=3)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    currency: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 2. AUTHENTICATION & TOKEN SCHEMAS
# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# ==========================================
# 3. SUBSCRIPTION SCHEMAS
# ==========================================

class SubscriptionBase(BaseModel):
    service_name: str = Field(..., min_length=2, max_length=100, example="Netflix")
    price: float = Field(..., gt=0, example=499.00)
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY)
    next_billing_date: date = Field(..., example="2026-11-01")
    category: Category = Field(default=Category.OTHER)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    auto_renew: bool = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    service_name: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    billing_cycle: Optional[BillingCycle] = None
    next_billing_date: Optional[date] = None
    category: Optional[Category] = None
    status: Optional[SubscriptionStatus] = None
    auto_renew: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime

    @computed_field
    def days_until_renewal(self) -> int:
        """Calculates days remaining until next billing date."""
        today = date.today()
        delta = (self.next_billing_date - today).days
        return delta

    @computed_field
    def urgency_level(self) -> str:
        """
        Determines renewal urgency for frontend badging:
        - 'urgent': <= 3 days remaining
        - 'upcoming': 4 to 7 days remaining
        - 'normal': > 7 days remaining
        """
        days = self.days_until_renewal
        if days <= 3:
            return "urgent"
        elif days <= 7:
            return "upcoming"
        return "normal"

    class Config:
        from_attributes = True

# ==========================================
# 4. DASHBOARD & ANALYTICS SCHEMAS
# ==========================================

class DashboardSummary(BaseModel):
    total_active_subscriptions: int
    total_cancelled_subscriptions: int
    monthly_burn_rate: float
    annual_spend: float
    upcoming_renewals_count: int  # Active subscriptions renewing within <= 7 days
    currency: str