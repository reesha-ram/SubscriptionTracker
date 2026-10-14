from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Subscriptions, Users, Category, SubscriptionStatus
from app.schemas import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse
)
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)

templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# ==========================================
# 1. JINJA2 WEB PAGE ROUTES
# ==========================================

@router.get("/manage-page", include_in_schema=False)
def render_subscriptions_page(request: Request, user: user_dependency):
    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={"user": user}
    )


@router.get("/add-page", include_in_schema=False)
def render_add_subscription_page(request: Request, user: user_dependency):
    return templates.TemplateResponse(
        request=request,
        name="add_subscription.html",
        context={"user": user}
    )


@router.get("/edit-page/{subscription_id}", include_in_schema=False)
def render_edit_subscription_page(
    subscription_id: int,
    request: Request,
    user: user_dependency,
    db: db_dependency
):
    subscription = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id,
        Subscriptions.user_id == user["id"]
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_subscription.html",
        context={"user": user, "subscription": subscription}
    )


# ==========================================
# 2. API ENDPOINTS (CRUD)
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubscriptionResponse)
def create_subscription(
    sub_data: SubscriptionCreate,
    user: user_dependency,
    db: db_dependency
):
    """Creates a new subscription for the authenticated user."""
    new_sub = Subscriptions(
        **sub_data.model_dump(),
        user_id=user["id"]
    )

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


@router.get("/", response_model=List[SubscriptionResponse])
def get_user_subscriptions(
    user: user_dependency,
    db: db_dependency,
    category: Optional[Category] = Query(None, description="Filter by category"),
    sub_status: Optional[SubscriptionStatus] = Query(None, alias="status", description="Filter by status")
):
    """Retrieves all subscriptions owned by the logged-in user with optional category/status filters."""
    query = db.query(Subscriptions).filter(Subscriptions.user_id == user["id"])

    if category:
        query = query.filter(Subscriptions.category == category)
    if sub_status:
        query = query.filter(Subscriptions.status == sub_status)

    return query.order_by(Subscriptions.next_billing_date.asc()).all()


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription_by_id(
    subscription_id: int,
    user: user_dependency,
    db: db_dependency
):
    """Gets a single subscription by ID ensuring user ownership."""
    sub = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id,
        Subscriptions.user_id == user["id"]
    ).first()

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found."
        )

    return sub


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    sub_data: SubscriptionUpdate,
    user: user_dependency,
    db: db_dependency
):
    """Updates an existing subscription record."""
    sub_query = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id,
        Subscriptions.user_id == user["id"]
    )
    sub = sub_query.first()

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found."
        )

    update_dict = sub_data.model_dump(exclude_unset=True)
    if update_dict:
        sub_query.update(update_dict, synchronize_session=False)
        db.commit()
        db.refresh(sub)

    return sub


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    user: user_dependency,
    db: db_dependency
):
    """Deletes a subscription record."""
    sub = db.query(Subscriptions).filter(
        Subscriptions.id == subscription_id,
        Subscriptions.user_id == user["id"]
    ).first()

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found."
        )

    db.delete(sub)
    db.commit()
    return None