from fastapi import APIRouter
from app.common.schemas import ValidationErrorLoggingRoute



router = APIRouter(route_class=ValidationErrorLoggingRoute)
prefix="",
tags=['']  

@router.get("/")
def get_list_of_todos():

    name = "testing the api router"
    return {"name": name}