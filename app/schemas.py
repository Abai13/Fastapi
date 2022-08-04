from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class BaseClass(BaseModel):
    class Config:
        orm_mode = True


class CategorySchema(BaseClass):
    title: str
    slug: str


class PostSchema(BaseClass):
    id: int
    title: str
    slug: str
    text: str
    category: CategorySchema

    class Config:
        schema_extra = {
            'example': {
                "id": 1,
                "title": "Первый выпускной в TSI AUCA",
                "slug": "pervyy_vypysknoy_v_tsi_auca",
                "text": "aahahahahlol",
                "category":
                    {
                     "title": "Новости",
                     "slug": "news"
                    }
            }
        }


class CreatePostSchema(BaseClass):
    title: str
    text: str
    category_id: str


class UpdatePostSchema(BaseClass):
    title: Optional[str]
    text: Optional[str]


class CreateUserSchema(BaseClass):
    email: EmailStr
    name: str
    password: str
    password_confirm: str

    @validator('password_confirm')
    def passwords_matching(cls, password_confirm, values, **kwargs):
        print(values)
        password = values.get('password')
        if password_confirm != password:
            raise ValueError('Пароли не совпадают')
        return password


class UserSchema(BaseClass):
    id: int
    email: EmailStr
    name: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenPayload(BaseModel):
    sub: str
    exp: int