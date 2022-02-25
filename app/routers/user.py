from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, utils
from ..database import conn, cursor
from psycopg2.errors import UniqueViolation


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    user.password = utils.hash(user.password)
    try:
        cursor.execute(
            """
            INSERT INTO users
            (email, password)
            VALUES
            (%s, %s)
            RETURNING *
            """,
            (user.email, user.password)
        )
    except UniqueViolation:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    created_user = cursor.fetchone()
    print(created_user)
    conn.commit()
    return created_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int):
    cursor.execute(
        """
        SELECT * FROM users
        WHERE id = %s;
        """,
        (str(id),)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exist.")
    return user
