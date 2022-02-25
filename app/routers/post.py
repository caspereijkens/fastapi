from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.params import Body
from .. import schemas, oauth2
from typing import List, Optional
from ..database import conn, cursor


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.Post])
def get_posts(search: Optional[str] = ""):
    cursor.execute(
        """
        SELECT posts.*, COUNT(votes.post_id) as votes
        FROM posts
        LEFT JOIN votes
        ON posts.id = votes.post_id
        WHERE content ILIKE %s
        GROUP BY posts.id
        ORDER BY created_at DESC;
        """,
        ("%" + search + "%",))
    posts = cursor.fetchall()
    return posts


@router.get("/user")
def get_user_posts(current_user: dict = Depends(oauth2.get_current_user)):
    cursor.execute(
        """
        SELECT * FROM posts
        where user_id = %s;
        """,
        (str(current_user.get("id")),)
    )
    posts = cursor.fetchall()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User does not have posts yet.")
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, user: dict = Depends(oauth2.get_current_user)):
    cursor.execute(
        """
        INSERT INTO posts (title, content, published, user_id) 
        VALUES (%s, %s, %s, %s)
        RETURNING *;
        """,
        (post.title, post.content, post.published, user.get("id"))
    )
    new_post = cursor.fetchone()
    conn.commit()
    return new_post


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, current_user = Depends(oauth2.get_current_user)):
    cursor.execute(
        """
        UPDATE posts
        SET title = %s, content = %s, published = %s, edited  = True
        WHERE id = %s
        RETURNING *;
        """,
        (post.title, post.content, post.published, str(id),)
    )
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist.")
    if updated_post.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Not authorized to perform requested action.")
    conn.commit()
    return updated_post


@router.get("/{id}")
def get_post(id: int):
    cursor.execute(
        """
        SELECT posts.*, COUNT(votes.post_id) as votes
        FROM posts
        LEFT JOIN votes
        ON posts.id = votes.post_id
        WHERE id = %s
        GROUP BY posts.id
        ORDER BY created_at DESC;
        """,
        (str(id),)
    )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist.")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user = Depends(oauth2.get_current_user)):
    cursor.execute(
        """
        SELECT * FROM posts
        WHERE id = %s;
        """,
        (str(id),)
    )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist.")
    if post.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Not authorized to perform requested action.")
    cursor.execute(
        """
        DELETE FROM posts
        WHERE id = %s;
        """,
        (str(id),)
    )
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
