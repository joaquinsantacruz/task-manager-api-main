from pydantic import BaseModel

# Lo que devuelve el endpoint de login
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Lo que contiene el token decodificado
class TokenPayload(BaseModel):
    sub: str | None = None