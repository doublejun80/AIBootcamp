"""
ContractGuard AI - 개선 제안 Agent
리스크 분석 기반 구체적 수정안 제시
"""
from typing import Any, Dict
import json
from langchain.schema import HumanMessage

from .base_agent import BaseAgent
from prompts.templates import PromptTemplates


class ImprovementAdvisorAgent(BaseAgent):
    """개선 제안 Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ImprovementAdvisor"
        self.description = "계약서 개선안 및 협상 전략 제안"
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """개선 제안 실행"""
        risk_result = input_data.get("risk_result", {})
        comparison_result = input_data.get("comparison_result", {})
        
        if not risk_result and not comparison_result:
            return {"error": "분석 결과가 없습니다."}
        
        # 결과를 문자열로 변환
        if isinstance(risk_result, dict):
            risk_str = json.dumps(risk_result, ensure_ascii=False, indent=2)
        else:
            risk_str = str(risk_result)
            
        if isinstance(comparison_result, dict):
            comparison_str = json.dumps(comparison_result, ensure_ascii=False, indent=2)
        else:
            comparison_str = str(comparison_result)
        
        # RAG로 개선 관련 컨텍스트 검색
        search_query = f"계약서 개선 제안 {risk_str[:200]}"
        context = self.retriever.get_context_for_analysis(search_query, "standard")
        
        # 프롬프트 생성
        prompt = PromptTemplates.IMPROVEMENT_ADVISOR.format(
            risk_result=risk_str,
            comparison_result=comparison_str,
            context=context
        )
        
        # LLM 호출
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # 응답 파싱
        result = self._parse_json_response(response.content)
        result["agent"] = self.name
        
        return result
    
    def get_tools(self) -> list:
        """개선 제안 전용 도구"""
        from langchain.tools import Tool
        
        tools = super().get_tools()
        tools.extend([
            Tool(
                name="suggest_alternative_clause",
                func=self._suggest_alternative,
                description="대체 조항 문구를 제안합니다."
            )
        ])
        return tools
    
    def _suggest_alternative(self, clause_type: str) -> str:
        """대체 조항 제안"""
        docs = self.retriever.search_standard_clause(clause_type, k=2)
        if docs:
            return f"표준 {clause_type} 조항 예시:\n" + docs[0].page_content[:500]
        return "대체 조항을 찾을 수 없습니다."

