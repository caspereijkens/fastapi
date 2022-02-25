from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from .database import conn, cursor
import json

with open("/etc/config_fastapi.json") as config_file:
    config = json.load(config_file)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(config["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=config["SECRET_KEY"], algorithm=config["ALGORITHM"])
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, config["SECRET_KEY"], algorithms=[config["ALGORITHM"]])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", 
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    cursor.execute(
        """
        SELECT * FROM users
        WHERE id = %s;
        """,
        (token.id,))
    user = cursor.fetchone()
    return user
