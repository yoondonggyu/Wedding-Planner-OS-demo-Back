from sqladmin import Admin, ModelView
from app.core.database import engine
from app.models.db import User, Post, Comment, PostLike, Tag

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.nickname, User.created_at]
    column_searchable_list = [User.email, User.nickname]

class PostAdmin(ModelView, model=Post):
    column_list = [Post.id, Post.title, Post.user_id, Post.board_type, Post.view_count, Post.created_at]
    column_searchable_list = [Post.title, Post.content]

class CommentAdmin(ModelView, model=Comment):
    column_list = [Comment.id, Comment.content, Comment.user_id, Comment.post_id, Comment.created_at]

class PostLikeAdmin(ModelView, model=PostLike):
    column_list = [PostLike.id, PostLike.post_id, PostLike.user_id, PostLike.created_at]

class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name]

def setup_admin(app):
    admin = Admin(app, engine, base_url="/secret_admin")
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(PostLikeAdmin)
    admin.add_view(TagAdmin)
