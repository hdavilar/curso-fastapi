from fastapi import APIRouter
from pydantic import BaseModel
from user_jwt import createToken
from fastapi.responses import JSONResponse

login_user = APIRouter()

#Clase user
class User(BaseModel):
    email: str
    passwd: str 


@login_user.post("/login", tags=["Autentificación"])
def login(user: User):
    if user.email == "email":
        token: str = createToken(dict(user))
        print(token)
        return JSONResponse(content=token)