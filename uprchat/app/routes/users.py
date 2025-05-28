from fastapi import APIRouter, Depends, status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from typing import Annotated
from sqlmodel import Session
from uprchat.app.database.db_config import get_session
from uprchat.app.users.schemas import UserCreate
from uprchat.app.users.services import register_user,login,get_user_data
from uprchat.app.users.utils import generate_token,get_current_user_uuid


rt = APIRouter(prefix="/users", tags=["users"])

oauth2 = OAuth2PasswordBearer(tokenUrl='login')


@rt.post('/login',response_model=dict,status_code=status.HTTP_200_OK)
async def login_user(session: Annotated[Session, Depends(get_session)],form: Annotated[OAuth2PasswordRequestForm,Depends()]):
    valid_credentials = await login()
    if(valid_credentials):
        user_data = get_user_data(username=form.username,session=session)
        user = UserCreate(username=form.username)
        if(user_data is None):
            result = await register_user(user_create=user,session=session)
            user_data = result
        access_token = generate_token(user_data.id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

@rt.get('/me')
async def me(token: Annotated[str,Depends(oauth2)]):
    uuid = get_current_user_uuid(token)
    return uuid

