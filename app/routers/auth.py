from fastapi import APIRouter, Depends, status, HTTPException, responses
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Authentication"],
)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid Credentials")
    
    if not utils.verfiy(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid Credentials")

    # create a token
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    # return a token
    return {"access_token": access_token, "token_type": "bearer"}