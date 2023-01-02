from fastapi import APIRouter, Depends

from apps import models
from . import utils
from apps.database import get_db
from .schemas import Users

from sqlalchemy.orm import Session

router = APIRouter(tags=["users"])

# @router.get("/")
# def test_user_router():
#     return "Endpoint is working"

# @router.post("/")
# def get_users():
#     return "Endpoint is working"

@router.post("/")
def register_user(form: Users, db:Session = Depends(get_db)):

    form.password = utils.get_password_hash(form.password)
    form.email = str(form.password).lower()

    add_user = models.Users(**form.__dict__)

    db.add(add_user)
    db.commit()
    db.refresh(add_user)
    return add_user

@router.put("/")
def update_user():
    return "Endpoint is working"

@router.delete("/")
def delete_user():
    return "Endpoint is working"