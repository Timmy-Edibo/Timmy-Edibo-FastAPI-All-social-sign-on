from pydantic import BaseModel

class Users(BaseModel):
    username: str
    email: str
    password: str

    class Meta:
        orm_mode = True