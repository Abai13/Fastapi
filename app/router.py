from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi_pagination import Page, paginate
from slugify import slugify
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_request_user, create_access_token, create_refresh_token
from app.database import get_db
from app.hashing import Hasher
from app.models import Category, Post, User, get_random_string, Tag
from app.schemas import CategorySchema, PostSchema, CreatePostSchema, UpdatePostSchema, CreateUserSchema, Token, \
    LoginSchema
from app.send_mail import send_email

router = APIRouter()


@router.get('/categories/', response_model=List[CategorySchema], status_code=status.HTTP_200_OK, tags=['categories'])
async def categories_list(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get('/posts/', response_model=Page[PostSchema], status_code=200, tags=['posts'])
async def posts_list(category: str = None, tag: str = None, q: str = None, db: Session = Depends(get_db)):
    """Возвращает список всех постов"""
    posts = db.query(Post)
    if category:
        posts = posts.filter(Post.category_id == category)
    if tag:
        # posts = posts.join(through_table).filter(through_table.columns.tag_id == tag)
        posts = posts.filter(Post.tags.any(Tag.slug == tag))
    if q:
        posts = posts.filter(or_(Post.title.ilike(f'%{q}%'), Post.text.ilike(f'%{q}%')))
    return paginate(posts.all())


@router.get('/posts/{slug}/', response_model=PostSchema, status_code=status.HTTP_200_OK, tags=['posts'])
async def post_details(slug, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if post is None:
        raise HTTPException(
            status_code=404,
            detail='Пост не найден'
        )
    return post


@router.post('/posts/', response_model=PostSchema, status_code=status.HTTP_201_CREATED, tags=['posts'])
async def create_post(data: CreatePostSchema,
                      db: Session = Depends(get_db),
                      user: User = Depends(get_request_user)):
    posts = [post[0] for post in db.query(Post).values('title')]
    if data.title in posts:
        return HTTPException(status_code=400,
                             detail='Пост с таким заголовком уже существует')
    slug = slugify(data.title)
    post = Post(author_id=user.id,
                slug=slug,
                **data.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch('/posts/{slug}/', response_model=PostSchema, status_code=status.HTTP_200_OK, tags=['posts'])
async def update_post(slug: str,
                      data: UpdatePostSchema,
                      db: Session = Depends(get_db),
                      user: User = Depends(get_request_user)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if post is None:
        raise HTTPException(status_code=404,
                            detail='Пост не найден')
    if post.author_id != user.id:
        raise HTTPException(status_code=403,
                            detail='Вы не являетесь автором')
    for key, value in data.dict().items():
        if value is not None:
            setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete('/posts/{slug}/', status_code=status.HTTP_204_NO_CONTENT, tags=['posts'])
async def delete_post(slug: str,
                      db: Session = Depends(get_db),
                      user: User = Depends(get_request_user)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if post is None:
        raise HTTPException(status_code=404,
                            detail='Пост не найден')
    if post.author_id != user.id:
        raise HTTPException(status_code=403,
                            detail='Вы не являетесь автором')
    db.delete(post)
    db.commit()
    return 'Пост удалён'


@router.post('/register/', status_code=status.HTTP_201_CREATED, tags=['auth'])
def register_user(background_task: BackgroundTasks,
                  user: CreateUserSchema,
                  db: Session = Depends(get_db)):
    emails = [u.email for u in db.query(User).all()]
    if user.email in emails:
        return HTTPException(
            status_code=400,
            detail='Email уже занят'
        )
    activation_code = get_random_string(8)
    hashed = Hasher.hash_password(user.password)
    user1 = User(**{'email': user.email, 'name': user.name})
    user1.password = hashed
    user1.activation_code = activation_code
    db.add(user1)
    db.commit()
    db.refresh(user1)
    send_email(
        background_task,
        'Активация аккаунта',
        user1.email,
        f'Для активации аккаунта перейдите по ссылке: http://localhost:8000/activate/{activation_code}/'
    )
    return user1


@router.get('/activate/{activation_code}/', status_code=status.HTTP_200_OK, tags=['auth'])
def activation(activation_code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.activation_code == activation_code).first()
    if user:
        user.activation_code = ''
        user.is_active = True
        db.commit()
        db.refresh(user)
        return 'Ваш аккаунт успешно активирован'
    else:
        raise HTTPException(status_code=404, detail='Пользователь не найден')


@router.post('/login/', response_model=Token, status_code=status.HTTP_200_OK, tags=['auth'])
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user is None:
        raise HTTPException(status_code=400,
                            detail='Неверный email')
    hashed_pass = user.password
    raw_pass = data.password
    if not Hasher.verify_password(raw_pass, hashed_pass):
        raise HTTPException(status_code=400,
                            detail='Неверный пароль')
    if not user.is_active:
        raise HTTPException(status_code=400,
                            detail='Аккаунт не активен')
    return {
        'access_token': create_access_token(str(user.id)),
        'refresh_token': create_refresh_token(str(user.id))
    }