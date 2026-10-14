from datetime import date, timedelta
from typing import Annotated, List
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Subscriptions, Users, BillingCycle, SubscriptionStatus
from app.schemas import DashboardSummary, SubscriptionResponse
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# ==========================================
# 1. JINJA2 WEB PAGE ROUTE
# ==========================================

@router.get("/", include_in_schema=False)
def render_dashboard_page(request: Request, user: user_dependency):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user}
    )


# ==========================================
# 2. ANALYTICS API ENDPOINTS
# ==========================================

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    user: user_dependency,
    db: db_dependency
):
    """
    Calculates real-time financial metrics for the active user:
    - Monthly Burn Rate
    - Projected Annual Spend
    - Active vs Cancelled counts
    - Upcoming Renewals (<= 7 days)
    """
    user_model = db.query(Users).filter(Users.id == user["id"]).first()
    currency = user_model.currency if user_model else "INR"

    subs = db.query(Subscriptions).filter(Subscriptions.user_id == user["id"]).all()

    active_subs = [s for s in subs if s.status == SubscriptionStatus.ACTIVE]
    cancelled_subs = [s for s in subs if s.status == SubscriptionStatus.CANCELLED]

    # Calculate Monthly Burn Rate
    monthly_burn = 0.0
    for sub in active_subs:
        price = float(sub.price)
        if sub.billing_cycle == BillingCycle.MONTHLY:
            monthly_burn += price
        elif sub.billing_cycle == BillingCycle.YEARLY:
            monthly_burn += price / 12.0

    annual_spend = monthly_burn * 12.0

    # Calculate upcoming renewals in next 7 days
    today = date.today()
    next_week = today + timedelta(days=7)
    upcoming_count = sum(
        1 for s in active_subs
        if today <= s.next_billing_date <= next_week
    )

    return DashboardSummary(
        total_active_subscriptions=len(active_subs),
        total_cancelled_subscriptions=len(cancelled_subs),
        monthly_burn_rate=round(monthly_burn, 2),
        annual_spend=round(annual_spend, 2),
        upcoming_renewals_count=upcoming_count,
        currency=currency
    )


@router.get("/upcoming-renewals", response_model=List[SubscriptionResponse])
def get_upcoming_renewals(
    user: user_dependency,
    db: db_dependency
):
    """Returns active subscriptions renewing within the next 7 days."""
    today = date.today()
    next_week = today + timedelta(days=7)

    subs = db.query(Subscriptions).filter(
        Subscriptions.user_id == user["id"],
        Subscriptions.status == SubscriptionStatus.ACTIVE,
        Subscriptions.next_billing_date >= today,
        Subscriptions.next_billing_date <= next_week
    ).order_by(Subscriptions.next_billing_date.asc()).all()

    return subs