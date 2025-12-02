"""
ContractGuard AI - 기본 Agent 클래스
모든 Agent의 공통 기능 정의
"""
from typing import Any, Dict, Optional
from langchain_openai import AzureChatOpenAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from config.settings import azure_config
from rag.retriever import ContractRetriever


class BaseAgent:
    """기본 Agent 클래스"""
    
    def __init__(
        self, 
        model_name: str = None,
        temperature: float = 0.1,
        retriever: ContractRetriever = None
    ):
        self.model_name = model_name or azure_config.gpt4o_mini
        self.temperature = temperature
        self.retriever = retriever or ContractRetriever()
        
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_config.endpoint,
            api_key=azure_config.api_key,
            api_version=azure_config.api_version,
            azure_deployment=self.model_name,
            temperature=self.temperature
        )
    
    def get_tools(self) -> list:
        """Agent가 사용할 도구 정의 (하위 클래스에서 오버라이드)"""
        return [
            Tool(
                name="search_legal_knowledge",
                func=self._search_legal_knowledge,
                description="법률 조항, 표준계약서, 리스크 정보를 검색합니다."
            )
        ]
    
    def _search_legal_knowledge(self, query: str) -> str:
        """법률 지식 검색 도구"""
        return self.retriever.get_context_for_analysis(query, "general")
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 실행 (하위 클래스에서 구현)"""
        raise NotImplementedError
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        import json
        import re
        
        # JSON 블록 추출
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # JSON 블록이 없으면 전체 텍스트에서 시도
            json_str = response
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 파싱 실패시 원본 텍스트 반환
            return {"raw_response": response}

