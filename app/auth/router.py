from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.auth.schemas import UserLogin, UserRegister
from app.auth.service import authenticate, create_session, create_user, get_user_by_session
from app.database import get_db

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = create_user(db, data.login, data.password)
    except ValueError:
        raise HTTPException(400, "user already exists")

    session_id = create_session(user.id)

    response = Response(content="registered")
    response.set_cookie("session_id", session_id)

    return response


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate(db, data.login, data.password)

    if not user:
        raise HTTPException(401, "wrong login or password")

    session_id = create_session(user.id)

    response = Response(content="logged in")
    response.set_cookie("session_id", session_id)

    return response


@router.get("/me")
def me(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401)

    user_id = get_user_by_session(session_id)
    if not user_id:
        raise HTTPException(401)

    return {"user_id": user_id}
