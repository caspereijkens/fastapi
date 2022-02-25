from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import conn, cursor
from .. import schemas, utils, oauth2

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    cursor.execute(
        """
        SELECT * FROM users
        WHERE email = %s;
        """, 
        (user_credentials.username,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(plain_password=user_credentials.password, hashed_password=user["password"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user["id"]})

    return {"access_token": access_token, "token_type": "bearer"} 