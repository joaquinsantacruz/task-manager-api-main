from pydantic import BaseModel, Field

class ChangeOwnerRequest(BaseModel):
    owner_id: int = Field(
        gt=0,
        description="ID of the new owner (must be a positive integer)"
    )
