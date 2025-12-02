"""
기본 청첩장 템플릿 데이터 생성 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.db import InvitationTemplate, InvitationTemplateStyle

def create_default_templates():
    """기본 템플릿 생성"""
    db = SessionLocal()
    
    try:
        # 기존 템플릿 확인
        existing = db.query(InvitationTemplate).count()
        if existing > 0:
            print(f"이미 {existing}개의 템플릿이 존재합니다. 건너뜁니다.")
            return
        
        templates = [
            {
                "name": "클래식 엘레강스",
                "style": InvitationTemplateStyle.CLASSIC,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#F5F5DC",
                    "text_color": "#2C2C2C",
                    "font_name": "Times New Roman",
                    "font_size": 14,
                    "layout": "centered"
                }
            },
            {
                "name": "모던 미니멀",
                "style": InvitationTemplateStyle.MODERN,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#FFFFFF",
                    "text_color": "#1A1A1A",
                    "font_name": "Helvetica",
                    "font_size": 12,
                    "layout": "minimal"
                }
            },
            {
                "name": "빈티지 로맨틱",
                "style": InvitationTemplateStyle.VINTAGE,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#FFF8E7",
                    "text_color": "#4A4A4A",
                    "font_name": "Georgia",
                    "font_size": 13,
                    "layout": "vintage"
                }
            },
            {
                "name": "럭셔리 골드",
                "style": InvitationTemplateStyle.LUXURY,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#1A1A1A",
                    "text_color": "#D4AF37",
                    "font_name": "Garamond",
                    "font_size": 14,
                    "layout": "luxury"
                }
            },
            {
                "name": "자연스러운 그린",
                "style": InvitationTemplateStyle.NATURE,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#F0F8F0",
                    "text_color": "#2D5016",
                    "font_name": "Arial",
                    "font_size": 13,
                    "layout": "nature"
                }
            },
            {
                "name": "로맨틱 핑크",
                "style": InvitationTemplateStyle.ROMANTIC,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#FFF0F5",
                    "text_color": "#8B4A6B",
                    "font_name": "Brush Script MT",
                    "font_size": 13,
                    "layout": "romantic"
                }
            },
            {
                "name": "심플 미니멀",
                "style": InvitationTemplateStyle.MINIMAL,
                "preview_image_url": None,
                "template_data": {
                    "background_color": "#FFFFFF",
                    "text_color": "#000000",
                    "font_name": "Arial",
                    "font_size": 11,
                    "layout": "minimal"
                }
            }
        ]
        
        for template_data in templates:
            template = InvitationTemplate(**template_data)
            db.add(template)
        
        db.commit()
        print(f"✅ {len(templates)}개의 기본 템플릿이 생성되었습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 템플릿 생성 실패: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_templates()

