from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models.admin_user import AdminUser
from app.services.audit_logger import AuditLogger
from app.utils.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str
    user_name: str


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: DbSession,
) -> LoginResponse:
    audit = AuditLogger(db)
    ip = request.client.host if request.client else None

    result = await db.execute(
        select(AdminUser).where(AdminUser.email == data.email)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.hashed_password):
        await audit.log(
            action="FAILED_LOGIN",
            ip_address=ip,
            metadata={"email": data.email},
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤，請重試",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已停用，請聯繫管理員",
        )

    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        remember_me=data.remember_me,
    )

    await audit.log(
        action="LOGIN",
        user=user,
        ip_address=ip,
    )
    await db.commit()

    return LoginResponse(
        access_token=token,
        user_email=user.email,
        user_name=user.display_name,
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> dict:
    audit = AuditLogger(db)
    ip = request.client.host if request.client else None
    await audit.log(action="LOGOUT", user=current_user, ip_address=ip)
    await db.commit()
    return {"message": "您已成功登出"}


@router.get("/me")
async def get_current_user_info(current_user: CurrentUser) -> dict:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
    }
