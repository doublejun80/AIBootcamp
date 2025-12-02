"""
ContractGuard AI - Retriever 모듈
계약서 분석을 위한 지식 검색
"""
from typing import List, Dict, Any
from langchain.schema import Document
from .vectorstore import VectorStoreManager


class ContractRetriever:
    """계약서 분석용 지식 검색기"""
    
    def __init__(self, vectorstore_manager: VectorStoreManager = None):
        if vectorstore_manager is None:
            vectorstore_manager = VectorStoreManager()
            vectorstore_manager.load_vectorstore()
        self.vs_manager = vectorstore_manager
    
    def search_legal_basis(self, clause_text: str, k: int = 3) -> List[Document]:
        """조항에 대한 법률적 근거 검색"""
        query = f"다음 계약 조항과 관련된 법률 조항 및 리스크: {clause_text}"
        return self.vs_manager.similarity_search(query, k=k)
    
    def search_standard_clause(self, clause_type: str, k: int = 3) -> List[Document]:
        """표준 조항 검색"""
        query = f"{clause_type}에 대한 표준계약서 조항"
        return self.vs_manager.similarity_search(query, k=k)
    
    def search_risk_keywords(self, text: str, k: int = 5) -> List[Document]:
        """리스크 키워드 관련 정보 검색"""
        query = f"계약서 리스크 체크리스트: {text}"
        return self.vs_manager.similarity_search(query, k=k)
    
    def get_context_for_analysis(
        self, 
        contract_text: str, 
        analysis_type: str = "general"
    ) -> str:
        """분석 유형에 따른 컨텍스트 생성"""
        
        if analysis_type == "risk":
            docs = self.search_risk_keywords(contract_text, k=5)
        elif analysis_type == "legal":
            docs = self.search_legal_basis(contract_text, k=5)
        elif analysis_type == "standard":
            docs = self.search_standard_clause(contract_text, k=5)
        else:
            # 일반 분석 - 모든 유형 검색
            docs = self.vs_manager.similarity_search(contract_text, k=5)
        
        if not docs:
            return "관련 지식 정보를 찾을 수 없습니다."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            doc_type = doc.metadata.get("type", "unknown")
            context_parts.append(
                f"[참조 {i}] ({doc_type})\n{doc.page_content[:500]}..."
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def format_retrieval_result(self, documents: List[Document]) -> Dict[str, Any]:
        """검색 결과 포맷팅"""
        return {
            "count": len(documents),
            "sources": [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "type": doc.metadata.get("type", "unknown")
                }
                for doc in documents
            ]
        }

