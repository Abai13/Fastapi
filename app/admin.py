from sqladmin import ModelAdmin

from app.models import Category, Post, User, Tag


class CategoryAdmin(ModelAdmin, model=Category):
    form_columns = [Category.title, Category.slug]
    form_include_pk = True


class TagAdmin(ModelAdmin, model=Tag):
    form_columns = [Tag.title, Tag.slug]
    form_include_pk = True


class PostAdmin(ModelAdmin, model=Post):
    form_columns = [Post.title, Post.slug, Post.text, Post.category, Post.author, Post.tags]


class UserAdmin(ModelAdmin, model=User):
    form_columns = [User.email, User.name, User.password, User.is_active]