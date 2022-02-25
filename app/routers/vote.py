from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, utils, oauth2
from ..database import conn, cursor
from psycopg2.errors import UniqueViolation


router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: dict = Depends(oauth2.get_current_user)):
    cursor.execute(
        """
        SELECT * FROM posts
        WHERE id = %s;
        """,
        (str(vote.post_id),)
    )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {vote.post_id} does not exist.")
    user_id = current_user.get("id")
    cursor.execute(
        """
        SELECT * FROM votes
        WHERE post_id = %s
        AND user_id = %s;
        """,
        (str(vote.post_id), str(user_id))
    )
    found_vote = cursor.fetchone()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {user_id} already voted on post {vote.post_id}.")
        cursor.execute(
            """
            INSERT INTO votes (post_id, user_id)
            VALUES (%s, %s)
            RETURNING *;
            """,
            (str(vote.post_id), str(user_id))
        )
        conn.commit()
        return {"message": "Successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {user_id} did not yet vote on post {vote.post_id}.")
        cursor.execute(
            """
            DELETE FROM votes 
            WHERE post_id = %s
            AND user_id = %s
            """,
            (str(vote.post_id), str(user_id))
        )
        conn.commit()
        return {"message": "Successfully removed vote"}

