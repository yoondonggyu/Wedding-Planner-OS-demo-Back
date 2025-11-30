"""
LangGraph 파이프라인 서비스 - 확장 가능한 구조 (나중에 구현 예정)

이 모듈은 LangGraph 파이프라인을 위한 인터페이스와 구조를 제공합니다.
실제 LangGraph 구현은 나중에 추가할 수 있도록 확장 가능한 구조로 설계되었습니다.
"""
from typing import Dict, List, Optional, Any
from enum import Enum


class IntentType(str, Enum):
    """의도 타입"""
    CALENDAR = "calendar"
    BUDGET = "budget"
    TODO = "todo"
    POST = "post"
    QUERY = "query"
    RECOMMENDATION = "recommendation"


class ActionType(str, Enum):
    """액션 타입"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"


class PipelineNode:
    """파이프라인 노드 (나중에 LangGraph Node로 변환 가능)"""
    
    def __init__(self, name: str, handler: callable):
        self.name = name
        self.handler = handler
    
    async def execute(self, state: Dict) -> Dict:
        """노드 실행"""
        try:
            result = await self.handler(state)
            return result
        except Exception as e:
            print(f"⚠️ 파이프라인 노드 실행 실패 ({self.name}): {e}")
            return {"error": str(e)}


class OrganizePipeline:
    """
    자동 정리 파이프라인 (LangGraph 구조 준비)
    
    현재는 단순 함수 호출로 작동하지만, 나중에 LangGraph로 전환 가능한 구조
    """
    
    def __init__(self):
        self.nodes: Dict[str, PipelineNode] = {}
        self._initialized = False
    
    def add_node(self, name: str, handler: callable):
        """노드 추가"""
        self.nodes[name] = PipelineNode(name, handler)
    
    async def execute(self, intent: str, action: str, entities: Dict, user_id: int) -> Dict:
        """
        파이프라인 실행
        
        Args:
            intent: 의도 타입
            action: 액션 타입
            entities: 추출된 엔티티
            user_id: 사용자 ID
        
        Returns:
            실행 결과
        """
        # 현재는 단순 함수 호출로 작동
        # 나중에 LangGraph StateGraph로 변환 가능
        
        state = {
            "intent": intent,
            "action": action,
            "entities": entities,
            "user_id": user_id,
            "results": []
        }
        
        # 의도에 따라 적절한 노드 실행
        node_name = f"{intent}_{action}"
        if node_name in self.nodes:
            result = await self.nodes[node_name].execute(state)
            return result
        
        # 기본 처리
        return {
            "success": False,
            "message": f"처리할 수 없는 의도/액션 조합: {intent}/{action}"
        }


# 전역 파이프라인 인스턴스
_organize_pipeline = None


def get_organize_pipeline() -> OrganizePipeline:
    """자동 정리 파이프라인 인스턴스 반환 (싱글톤)"""
    global _organize_pipeline
    
    if _organize_pipeline is None:
        _organize_pipeline = OrganizePipeline()
        _initialize_pipeline(_organize_pipeline)
    
    return _organize_pipeline


def _initialize_pipeline(pipeline: OrganizePipeline):
    """
    파이프라인 초기화 (노드 등록)
    
    나중에 LangGraph로 전환할 때 이 부분을 StateGraph로 변환하면 됩니다.
    """
    # 현재는 빈 구조만 준비
    # 나중에 LangGraph 구현 시 여기에 노드들을 추가
    
    async def calendar_create_handler(state: Dict) -> Dict:
        """캘린더 일정 생성 핸들러 (예시)"""
        # 실제 구현은 나중에 LangGraph로 전환
        return {
            "success": True,
            "type": "calendar_event",
            "message": "캘린더 일정 생성 (LangGraph 구현 예정)"
        }
    
    async def budget_create_handler(state: Dict) -> Dict:
        """예산 항목 생성 핸들러 (예시)"""
        return {
            "success": True,
            "type": "budget_item",
            "message": "예산 항목 생성 (LangGraph 구현 예정)"
        }
    
    # 노드 등록 (나중에 LangGraph StateGraph로 변환)
    # pipeline.add_node("calendar_create", calendar_create_handler)
    # pipeline.add_node("budget_create", budget_create_handler)
    
    print("✅ 자동 정리 파이프라인 구조 초기화 완료 (LangGraph 구현 준비됨)")


async def run_organize_pipeline(
    intent: str,
    action: str,
    entities: Dict,
    user_id: int
) -> Dict:
    """
    자동 정리 파이프라인 실행 (외부 호출용)
    
    Args:
        intent: 의도 타입
        action: 액션 타입
        entities: 추출된 엔티티
        user_id: 사용자 ID
    
    Returns:
        실행 결과
    """
    pipeline = get_organize_pipeline()
    return await pipeline.execute(intent, action, entities, user_id)


# LangGraph 전환을 위한 유틸리티 함수들
def prepare_langgraph_state(intent: str, action: str, entities: Dict, user_id: int) -> Dict:
    """
    LangGraph State 준비 (나중에 사용)
    
    LangGraph로 전환할 때 이 함수를 사용하여 초기 State를 생성할 수 있습니다.
    """
    return {
        "intent": intent,
        "action": action,
        "entities": entities,
        "user_id": user_id,
        "results": [],
        "errors": []
    }


def extract_langgraph_result(state: Dict) -> Dict:
    """
    LangGraph State에서 결과 추출 (나중에 사용)
    
    LangGraph로 전환할 때 이 함수를 사용하여 최종 결과를 추출할 수 있습니다.
    """
    return {
        "success": len(state.get("errors", [])) == 0,
        "results": state.get("results", []),
        "errors": state.get("errors", [])
    }

