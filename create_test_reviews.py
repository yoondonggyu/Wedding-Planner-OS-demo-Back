"""
테스트 후기 데이터 생성 스크립트
10개 카테고리에 각각 다른 후기를 작성합니다.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.db import Post, User
from app.core.categories import ALL_CATEGORIES
import random
from datetime import datetime

# 테스트 후기 템플릿
REVIEW_TEMPLATES = [
    "별로다",
    "그저 그렇다",
    "좋다",
    "너무 좋다",
    "이쁘다",
    "괜찮다",
    "다신 안 간다",
    "결혼을 다시할만큼 좋다",
    "이 업체라면 결혼 한번더?",
    "쏘쏘"
]

def create_test_reviews():
    """10개 카테고리에 테스트 후기 생성"""
    db = next(get_db())
    
    try:
        # 첫 번째 사용자 가져오기 (없으면 생성)
        user = db.query(User).first()
        if not user:
            print("❌ 사용자가 없습니다. 먼저 회원가입을 해주세요.")
            return
        
        print(f"✅ 사용자 ID: {user.id}, 닉네임: {user.nickname}")
        
        # 10개 카테고리 랜덤 선택
        selected_categories = random.sample(ALL_CATEGORIES, min(10, len(ALL_CATEGORIES)))
        
        print(f"\n📝 {len(selected_categories)}개 카테고리에 후기 생성 중...")
        
        created_posts = []
        for i, category in enumerate(selected_categories):
            review_text = REVIEW_TEMPLATES[i % len(REVIEW_TEMPLATES)]
            
            # 카테고리에 맞는 제목 생성
            from app.core.categories import get_category_display_name
            category_display = get_category_display_name(category)
            
            title = f"{category_display} 후기"
            content = f"{review_text}\n\n{category_display}에 대한 솔직한 후기입니다."
            
            post = Post(
                user_id=user.id,
                title=title,
                content=content,
                board_type="couple",
                category=category,
                view_count=random.randint(0, 100),
                created_at=datetime.now()
            )
            
            db.add(post)
            created_posts.append({
                "category": category_display,
                "review": review_text,
                "title": title
            })
        
        db.commit()
        
        print("\n✅ 테스트 후기 생성 완료!")
        print("\n생성된 후기 목록:")
        for i, post_info in enumerate(created_posts, 1):
            print(f"{i}. [{post_info['category']}] {post_info['title']} - {post_info['review']}")
        
        return created_posts
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_reviews()


