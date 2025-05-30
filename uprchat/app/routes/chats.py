from fastapi import APIRouter, Depends, status, HTTPException,Request
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from uprchat.app.chats.schemas import ChatDB
from uprchat.app.chats.services import create_chat, read_all_chats, read_chat, delete_chat
from uprchat.app.database.db_config import get_session
from uprchat.app.users.utils import get_current_user_uuid
from uprchat.app.routes.users import oauth2
from uuid import UUID


rt = APIRouter(prefix="/chats", tags=["chats"])


@rt.post("/",status_code=status.HTTP_201_CREATED,response_model=ChatDB)
async def create_new_chat(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str,Depends(oauth2)]
):
    user_id = get_current_user_uuid(token)
    return await create_chat(user_id=UUID(user_id),session=session)

@rt.get('/',status_code=status.HTTP_200_OK,response_model=list[ChatDB])
async def get_all_chats( token: Annotated[str,Depends(oauth2)],session: Annotated[AsyncSession,Depends(get_session)], offset: int = 0, limit: int = 100):
    user_id = get_current_user_uuid(token)
    return await read_all_chats(session=session,offset=offset, limit=limit, user_id=UUID(user_id))

@rt.get('/{chat_id}',status_code=status.HTTP_200_OK,response_model=ChatDB)
async def get_one_chat(chat_id: int ,session: Annotated[AsyncSession,Depends(get_session)]):
    result = await read_chat(chat_id=chat_id,session=session)
    if(result is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Chat not found")
    return result

@rt.delete('/{chat_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_chat(chat_id: int ,session: Annotated[AsyncSession,Depends(get_session)]):
    return await delete_chat(chat_id=chat_id,session=session)

@rt.post('/prompt')
async def prompt():
    return {"text":"""Aquí hay algún texto y luego un formulario en JSON:
            
  {
  "formAttributes": {
    "id": "my-form",
    "class": "custom-form",
    "data-validate": "true"
  },
  "fields": [
    {
      "type": "text",
      "name": "username",
      "label": "Nombre de usuario",
      "placeholder": "Ingresa tu nombre",
      "required": true
    },
    {
      "type": "email",
      "name": "email",
      "label": "Correo electrónico",
      "placeholder": "tu@email.com",
      "required": true
    },
    {
      "type": "select",
      "name": "country",
      "label": "País",
      "options": [
        { "value": "mx", "label": "México" },
        { "value": "us", "label": "Estados Unidos" },
        { "value": "es", "label": "España" }
      ]
    },
    {
      "type": "radio",
      "name": "gender",
      "label": "Género",
      "options": [
        { "value": "male", "label": "Masculino" },
        { "value": "female", "label": "Femenino" },
        { "value": "other", "label": "Otro" }
      ],
      "required": true
    },
    {
      "type": "checkbox",
      "name": "interests",
      "label": "Intereses",
      "options": [
        { "value": "sports", "label": "Deportes" },
        { "value": "music", "label": "Música" },
        { "value": "technology", "label": "Tecnología" },
        { "value": "travel", "label": "Viajes" }
      ]
    },
    {
      "type": "checkbox",
      "name": "terms",
      "label": "Acepto los términos y condiciones",
      "required": true
    },
    {
      "type": "textarea",
      "name": "comments",
      "label": "Comentarios",
      "placeholder": "Escribe tus comentarios aquí..."
    }
  ]
}
            
  Y luego más texto después del JSON. \n # Hola mundo \n - Element \n - Element \n ```java\nwhile (i < 5) {\n console.log(\"hi\");\n i+= 1;\n}\n``` \n
            """,

            "files":[{
        "src":"data:image/jpeg;base64,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",
        "type":"image"
    },{
        "name":"Libro",
        "src":"https://www.colomos.ceti.mx/documentos/goe/los7HabitosGenteAltamenteEfectiva.pdf",
        "type":"pdf"
    }]}

@rt.post('/query')
async def query(request: Request):
    print(request.body)
    return {
        "text":"Respuesta de prueba"
    }