"""
ContractGuard AI - 리스크 평가 Agent
계약서의 잠재적 리스크 식별 및 평가
"""
from typing import Any, Dict
import json
from langchain.schema import HumanMessage

from .base_agent import BaseAgent
from prompts.templates import PromptTemplates


class RiskEvaluatorAgent(BaseAgent):
    """리스크 평가 Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "RiskEvaluator"
        self.description = "계약서 리스크 식별 및 평가"
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 평가 실행"""
        contract_text = input_data.get("contract_text", "")
        analysis_result = input_data.get("analysis_result", {})
        
        if not contract_text:
            return {"error": "계약서 텍스트가 없습니다."}
        
        # RAG로 리스크 관련 컨텍스트 검색
        context = self.retriever.get_context_for_analysis(
            contract_text[:1000],
            "risk"
        )
        
        # 분석 결과를 문자열로 변환
        if isinstance(analysis_result, dict):
            analysis_str = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        else:
            analysis_str = str(analysis_result)
        
        # 프롬프트 생성
        prompt = PromptTemplates.RISK_EVALUATOR.format(
            analysis_result=analysis_str,
            contract_text=contract_text,
            context=context
        )
        
        # LLM 호출
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # 응답 파싱
        result = self._parse_json_response(response.content)
        result["agent"] = self.name
        
        # 리스크 점수 검증
        if "risk_score" in result:
            result["risk_score"] = max(0, min(100, int(result.get("risk_score", 50))))
        
        return result
    
    def get_tools(self) -> list:
        """리스크 평가 전용 도구"""
        from langchain.tools import Tool
        
        tools = super().get_tools()
        tools.extend([
            Tool(
                name="check_damage_clause",
                func=self._check_damage_clause,
                description="손해배상 조항의 리스크를 체크합니다."
            ),
            Tool(
                name="check_termination_clause",
                func=self._check_termination_clause,
                description="계약해지 조항의 리스크를 체크합니다."
            )
        ])
        return tools
    
    def _check_damage_clause(self, text: str) -> str:
        """손해배상 조항 체크"""
        risk_indicators = [
            ("무제한", "손해배상 한도 없음 - 고위험"),
            ("간접손해", "간접손해 포함 - 주의 필요"),
            ("특별손해", "특별손해 포함 - 주의 필요"),
            ("예정액", "위약금 예정액 확인 필요"),
        ]
        
        found_risks = []
        for indicator, description in risk_indicators:
            if indicator in text:
                found_risks.append(description)
        
        return "; ".join(found_risks) if found_risks else "특별한 리스크 없음"
    
    def _check_termination_clause(self, text: str) -> str:
        """계약해지 조항 체크"""
        risk_indicators = [
            ("일방적", "일방적 해지권 - 주의 필요"),
            ("즉시", "즉시 해지 가능 - 고위험"),
            ("사전 통지 없이", "사전 통지 없는 해지 - 고위험"),
        ]
        
        found_risks = []
        for indicator, description in risk_indicators:
            if indicator in text:
                found_risks.append(description)
        
        return "; ".join(found_risks) if found_risks else "특별한 리스크 없음"

