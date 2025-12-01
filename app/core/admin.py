from sqladmin import Admin, ModelView
from app.core.database import engine
from app.models.db import User, Post, Comment, PostLike, Tag, CalendarEvent, WeddingDate, WeddingProfile, Vendor, FavoriteVendor, BudgetItem, UserTotalBudget, ChatHistory
from app.core.sql_terminal import SQLTerminalView

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.nickname, User.created_at]
    column_searchable_list = [User.email, User.nickname]
    form_columns = ["email", "password", "nickname", "profile_image_url"]

class PostAdmin(ModelView, model=Post):
    column_list = [Post.id, Post.title, Post.user_id, Post.board_type, Post.view_count, Post.created_at]
    column_searchable_list = [Post.title, Post.content]
    form_columns = ["user", "title", "content", "image_url", "board_type"]

class CommentAdmin(ModelView, model=Comment):
    column_list = [Comment.id, Comment.content, Comment.user_id, Comment.post_id, Comment.created_at]
    form_columns = ["post_id", "user_id", "content"]

class PostLikeAdmin(ModelView, model=PostLike):
    column_list = [PostLike.id, PostLike.post_id, PostLike.user_id, PostLike.created_at]
    form_columns = ["post_id", "user_id"]

class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name]

class CalendarEventAdmin(ModelView, model=CalendarEvent):
    # ENUM 필드(priority, assignee)는 column_list에서 제외하여 오류 방지
    column_list = [CalendarEvent.id, CalendarEvent.title, CalendarEvent.user_id, CalendarEvent.start_date, CalendarEvent.category, CalendarEvent.is_completed]
    column_searchable_list = [CalendarEvent.title, CalendarEvent.description]
    # ENUM 필드는 form에서 제외
    form_columns = ["user", "title", "description", "start_date", "end_date", "start_time", "end_time", "location", "category", "progress", "is_completed"]

# TodoAdmin 제거됨 - calendar_events 테이블의 category='todo'로 통합됨

class WeddingDateAdmin(ModelView, model=WeddingDate):
    column_list = [WeddingDate.user_id, WeddingDate.wedding_date, WeddingDate.dday_offset]
    form_columns = ["user", "wedding_date", "dday_offset"]

class WeddingProfileAdmin(ModelView, model=WeddingProfile):
    column_list = [WeddingProfile.id, WeddingProfile.user_id, WeddingProfile.wedding_date, WeddingProfile.guest_count_category, WeddingProfile.total_budget]
    column_searchable_list = [WeddingProfile.location_city, WeddingProfile.location_district]
    form_columns = ["user", "wedding_date", "guest_count_category", "total_budget", "location_city", "location_district", "style_indoor", "style_outdoor", "outdoor_rain_plan_required"]

class VendorAdmin(ModelView, model=Vendor):
    column_list = [Vendor.id, Vendor.name, Vendor.vendor_type, Vendor.base_location_city, Vendor.min_price, Vendor.max_price, Vendor.rating_avg]
    column_searchable_list = [Vendor.name, Vendor.description]
    form_columns = ["vendor_type", "name", "description", "base_location_city", "base_location_district", "service_area", "min_price", "max_price", "rating_avg", "review_count", "portfolio_images", "portfolio_videos", "contact_link", "contact_phone", "tags"]

class FavoriteVendorAdmin(ModelView, model=FavoriteVendor):
    column_list = [FavoriteVendor.id, FavoriteVendor.user_id, FavoriteVendor.wedding_profile_id, FavoriteVendor.vendor_id, FavoriteVendor.created_at]
    form_columns = ["user_id", "wedding_profile_id", "vendor_id"]

class BudgetItemAdmin(ModelView, model=BudgetItem):
    column_list = [BudgetItem.id, BudgetItem.user_id, BudgetItem.item_name, BudgetItem.category, BudgetItem.estimated_budget, BudgetItem.actual_expense, BudgetItem.created_at]
    column_searchable_list = [BudgetItem.item_name, BudgetItem.notes]
    form_columns = ["user", "item_name", "category", "estimated_budget", "actual_expense", "quantity", "unit", "payer", "notes"]

class UserTotalBudgetAdmin(ModelView, model=UserTotalBudget):
    column_list = [UserTotalBudget.user_id, UserTotalBudget.total_budget, UserTotalBudget.updated_at]
    form_columns = ["user", "total_budget"]

class ChatHistoryAdmin(ModelView, model=ChatHistory):
    column_list = [ChatHistory.id, ChatHistory.user_id, ChatHistory.role, ChatHistory.content, ChatHistory.created_at]
    column_searchable_list = [ChatHistory.content]
    form_columns = ["user", "role", "content"]

def setup_admin(app):
    admin = Admin(app, engine, base_url="/secret_admin")
    admin.add_view(UserAdmin)
    admin.add_view(PostAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(PostLikeAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(CalendarEventAdmin)
    # TodoAdmin 제거됨 - calendar_events 테이블의 category='todo'로 통합됨
    admin.add_view(WeddingDateAdmin)
    admin.add_view(WeddingProfileAdmin)
    admin.add_view(VendorAdmin)
    admin.add_view(FavoriteVendorAdmin)
    admin.add_view(BudgetItemAdmin)
    admin.add_view(UserTotalBudgetAdmin)
    admin.add_view(ChatHistoryAdmin)
    # admin.add_view(SQLTerminalView)  # SQL 터미널 - BaseView 구현 문제로 임시 비활성화
