
from .. import schemas, models, oauth2
from fastapi import FastAPI, HTTPException, status, Response, Depends, APIRouter
from fastapi.params import Body
from typing import List, Optional
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    prefix= "/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
def post(db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user), Limit: int = 5, skip: int = 0, search: Optional [str] = ""):

    # post = db.query(models.Post).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(Limit).offset(skip).all()
    
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post : schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
  
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print("I am in the function")
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        print("ininin")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f'ID {id} is not found')
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post Not Found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user is not authorized to delete the post")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return status.HTTP_204_NO_CONTENT

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),  user_id: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title= %s, content=%s, published=%s WHERE id = %s RETURNING *""", (post.title,post.content,post.published,str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    query_post = db.query(models.Post).filter(models.Post.id == id)
    post = query_post.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    if post.owner_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user is not authorized to update the post")
    
   
    query_post.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return query_post.first()