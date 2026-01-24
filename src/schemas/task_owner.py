from pydantic import BaseModel

class ChangeOwnerRequest(BaseModel):
    owner_id: int
