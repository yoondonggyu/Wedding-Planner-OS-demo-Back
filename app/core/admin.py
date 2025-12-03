from sqladmin import Admin, ModelView
from app.core.database import engine
from app.models.db import (
    User, Post, Comment, PostLike, Tag, CalendarEvent, WeddingDate, WeddingProfile, 
    Vendor, FavoriteVendor, BudgetItem, UserTotalBudget, ChatHistory,
    Couple, VendorThread, VendorMessage, VendorContract, VendorDocument, VendorPaymentSchedule,
    InvitationTemplate, InvitationDesign, InvitationOrder,
    DigitalInvitation, Payment, RSVP, GuestMessage, ChatMemory
)
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

class CoupleAdmin(ModelView, model=Couple):
    column_list = [Couple.id, Couple.couple_key, Couple.user1_id, Couple.user2_id, Couple.status, Couple.connected_at]
    column_searchable_list = [Couple.couple_key]
    form_columns = ["couple_key", "user1_id", "user2_id", "status", "connected_at"]

class VendorThreadAdmin(ModelView, model=VendorThread):
    column_list = [VendorThread.id, VendorThread.user_id, VendorThread.vendor_id, VendorThread.title, VendorThread.is_active, VendorThread.last_message_at]
    column_searchable_list = [VendorThread.title]
    form_columns = ["user", "vendor", "title", "is_active", "is_shared_with_partner"]

class VendorMessageAdmin(ModelView, model=VendorMessage):
    column_list = [VendorMessage.id, VendorMessage.thread_id, VendorMessage.sender_type, VendorMessage.sender_id, VendorMessage.is_read, VendorMessage.created_at]
    column_searchable_list = [VendorMessage.content]
    form_columns = ["thread", "sender_type", "sender_id", "content", "is_read"]

class VendorContractAdmin(ModelView, model=VendorContract):
    column_list = [VendorContract.id, VendorContract.thread_id, VendorContract.user_id, VendorContract.vendor_id, VendorContract.total_amount, VendorContract.service_date]
    form_columns = ["thread", "user", "vendor", "contract_date", "total_amount", "deposit_amount", "interim_amount", "balance_amount", "service_date", "notes", "is_active"]

class VendorDocumentAdmin(ModelView, model=VendorDocument):
    column_list = [VendorDocument.id, VendorDocument.contract_id, VendorDocument.document_type, VendorDocument.version, VendorDocument.status, VendorDocument.file_name]
    column_searchable_list = [VendorDocument.file_name]
    form_columns = ["contract", "document_type", "version", "file_url", "file_name", "status", "signed_at", "signed_by"]

class VendorPaymentScheduleAdmin(ModelView, model=VendorPaymentSchedule):
    column_list = [VendorPaymentSchedule.id, VendorPaymentSchedule.contract_id, VendorPaymentSchedule.payment_type, VendorPaymentSchedule.amount, VendorPaymentSchedule.due_date, VendorPaymentSchedule.status]
    form_columns = ["contract", "payment_type", "amount", "due_date", "paid_date", "payment_method", "status", "reminder_sent", "notes"]

class InvitationTemplateAdmin(ModelView, model=InvitationTemplate):
    column_list = [InvitationTemplate.id, InvitationTemplate.name, InvitationTemplate.style, InvitationTemplate.is_active, InvitationTemplate.created_at]
    column_searchable_list = [InvitationTemplate.name]
    form_columns = ["name", "style", "preview_image_url", "template_data", "is_active"]

class InvitationDesignAdmin(ModelView, model=InvitationDesign):
    column_list = [InvitationDesign.id, InvitationDesign.user_id, InvitationDesign.template_id, InvitationDesign.status, InvitationDesign.created_at]
    form_columns = ["user", "template", "design_data", "status", "qr_code_url", "pdf_url", "preview_image_url"]

class InvitationOrderAdmin(ModelView, model=InvitationOrder):
    column_list = [InvitationOrder.id, InvitationOrder.design_id, InvitationOrder.user_id, InvitationOrder.quantity, InvitationOrder.order_status, InvitationOrder.total_price]
    form_columns = ["design", "user", "quantity", "paper_type", "paper_size", "total_price", "order_status", "vendor", "shipping_address", "shipping_phone", "shipping_name"]

class DigitalInvitationAdmin(ModelView, model=DigitalInvitation):
    column_list = [DigitalInvitation.id, DigitalInvitation.user_id, DigitalInvitation.invitation_url, DigitalInvitation.groom_name, DigitalInvitation.bride_name, DigitalInvitation.wedding_date, DigitalInvitation.view_count]
    column_searchable_list = [DigitalInvitation.invitation_url, DigitalInvitation.groom_name, DigitalInvitation.bride_name]
    form_columns = ["user", "invitation_design_id", "theme", "invitation_url", "groom_name", "bride_name", "wedding_date", "wedding_time", "wedding_location", "is_active"]

class PaymentAdmin(ModelView, model=Payment):
    column_list = [Payment.id, Payment.invitation_id, Payment.payer_name, Payment.amount, Payment.payment_method, Payment.payment_status, Payment.created_at]
    column_searchable_list = [Payment.payer_name]
    form_columns = ["invitation", "payer_name", "payer_phone", "payer_message", "amount", "payment_method", "payment_status", "transaction_id"]

class RSVPAdmin(ModelView, model=RSVP):
    column_list = [RSVP.id, RSVP.invitation_id, RSVP.guest_name, RSVP.status, RSVP.plus_one, RSVP.created_at]
    column_searchable_list = [RSVP.guest_name, RSVP.guest_phone]
    form_columns = ["invitation", "guest_name", "guest_phone", "guest_email", "status", "plus_one", "plus_one_name", "dietary_restrictions", "special_requests"]

class GuestMessageAdmin(ModelView, model=GuestMessage):
    column_list = [GuestMessage.id, GuestMessage.invitation_id, GuestMessage.guest_name, GuestMessage.is_approved, GuestMessage.created_at]
    column_searchable_list = [GuestMessage.guest_name, GuestMessage.message]
    form_columns = ["invitation", "guest_name", "guest_phone", "message", "image_url", "is_approved"]

class ChatMemoryAdmin(ModelView, model=ChatMemory):
    column_list = [ChatMemory.id, ChatMemory.user_id, ChatMemory.title, ChatMemory.created_at, ChatMemory.is_shared_with_partner]
    column_searchable_list = [ChatMemory.content, ChatMemory.title]
    form_columns = ["user", "content", "title", "tags", "is_shared_with_partner"]

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
    admin.add_view(CoupleAdmin)
    admin.add_view(VendorThreadAdmin)
    admin.add_view(VendorMessageAdmin)
    admin.add_view(VendorContractAdmin)
    admin.add_view(VendorDocumentAdmin)
    admin.add_view(VendorPaymentScheduleAdmin)
    admin.add_view(InvitationTemplateAdmin)
    admin.add_view(InvitationDesignAdmin)
    admin.add_view(InvitationOrderAdmin)
    admin.add_view(DigitalInvitationAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(RSVPAdmin)
    admin.add_view(GuestMessageAdmin)
    admin.add_view(ChatMemoryAdmin)
    # admin.add_view(SQLTerminalView)  # SQL 터미널 - BaseView 구현 문제로 임시 비활성화
