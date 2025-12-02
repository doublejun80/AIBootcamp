"""
ContractGuard AI - 계약 분석 Agent
계약서 유형 파악 및 핵심 조항 추출
"""
from typing import Any, Dict
from langchain_core.messages import HumanMessage

from .base_agent import BaseAgent
from prompts.templates import PromptTemplates


class ContractAnalyzerAgent(BaseAgent):
    """계약 분석 Agent"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ContractAnalyzer"
        self.description = "계약서 유형 파악 및 핵심 조항 추출"
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """계약서 분석 실행"""
        contract_text = input_data.get("contract_text", "")
        
        if not contract_text:
            return {"error": "계약서 텍스트가 없습니다."}
        
        # RAG로 컨텍스트 검색
        context = self.retriever.get_context_for_analysis(
            contract_text[:1000],  # 처음 1000자로 검색
            "general"
        )
        
        # 프롬프트 생성
        prompt = PromptTemplates.CONTRACT_ANALYZER.format(
            contract_text=contract_text,
            context=context
        )
        
        # LLM 호출
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # 응답 파싱
        result = self._parse_json_response(response.content)
        result["agent"] = self.name
        result["raw_text"] = contract_text
        
        return result
    
    def get_tools(self) -> list:
        """계약 분석 전용 도구"""
        from langchain.tools import Tool
        
        tools = super().get_tools()
        tools.extend([
            Tool(
                name="identify_contract_type",
                func=self._identify_type,
                description="계약서 유형을 식별합니다."
            ),
            Tool(
                name="extract_parties",
                func=self._extract_parties,
                description="계약 당사자 정보를 추출합니다."
            )
        ])
        return tools
    
    def _identify_type(self, text: str) -> str:
        """계약서 유형 식별"""
        from utils.text_processor import TextProcessor
        return TextProcessor.identify_contract_type(text)
    
    def _extract_parties(self, text: str) -> str:
        """계약 당사자 추출"""
        import re
        
        patterns = [
            r'"갑"[:\s]*([^"]+)',
            r'"을"[:\s]*([^"]+)',
            r'갑\s*:\s*([^\n]+)',
            r'을\s*:\s*([^\n]+)',
        ]
        
        parties = {}
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                party_type = "갑" if i < 2 else "을"
                parties[party_type] = match.group(1).strip()[:50]
        
        return str(parties) if parties else "당사자 정보를 찾을 수 없습니다."

