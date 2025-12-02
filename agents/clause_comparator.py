"""
ContractGuard AI - 조항 비교 Agent
표준계약서와 비교 분석
"""
from typing import Any, Dict
from langchain_core.messages import HumanMessage

from .base_agent import BaseAgent
from prompts.templates import PromptTemplates


class ClauseComparatorAgent(BaseAgent):
    """조항 비교 Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ClauseComparator"
        self.description = "표준계약서와 조항 비교"
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """조항 비교 실행"""
        contract_text = input_data.get("contract_text", "")
        contract_type = input_data.get("contract_type", "일반계약")
        
        if not contract_text:
            return {"error": "계약서 텍스트가 없습니다."}
        
        # RAG로 표준계약서 컨텍스트 검색
        context = self.retriever.get_context_for_analysis(
            f"{contract_type} 표준계약서 조항",
            "standard"
        )
        
        # 프롬프트 생성
        prompt = PromptTemplates.CLAUSE_COMPARATOR.format(
            contract_text=contract_text,
            context=context
        )
        
        # LLM 호출
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # 응답 파싱
        result = self._parse_json_response(response.content)
        result["agent"] = self.name
        result["compared_with"] = f"{contract_type} 표준계약서"
        
        return result
    
    def get_tools(self) -> list:
        """조항 비교 전용 도구"""
        from langchain.tools import Tool
        
        tools = super().get_tools()
        tools.extend([
            Tool(
                name="get_standard_template",
                func=self._get_standard_template,
                description="표준계약서 템플릿을 가져옵니다."
            )
        ])
        return tools
    
    def _get_standard_template(self, contract_type: str) -> str:
        """표준계약서 템플릿 가져오기"""
        docs = self.retriever.search_standard_clause(contract_type, k=3)
        if docs:
            return "\n\n".join([doc.page_content for doc in docs])
        return "표준계약서 템플릿을 찾을 수 없습니다."

