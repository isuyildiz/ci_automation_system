from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None


class RegisterResponse(BaseModel):
    id: str
    username: str
    email: str | None
