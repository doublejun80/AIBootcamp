"""
ContractGuard AI - Vector Store 관리 모듈
ChromaDB 기반 벡터 데이터베이스 관리
"""
import os
from typing import List, Optional
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import azure_config, app_config


class VectorStoreManager:
    """Vector Store 관리자"""
    
    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=azure_config.endpoint,
            api_key=azure_config.api_key,
            api_version=azure_config.api_version,
            azure_deployment=azure_config.embed_large
        )
        self.vectorstore: Optional[Chroma] = None
        self.persist_directory = app_config.vectorstore_dir
        
    def _get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """텍스트 분할기 반환"""
        return RecursiveCharacterTextSplitter(
            chunk_size=app_config.chunk_size,
            chunk_overlap=app_config.chunk_overlap,
            separators=["\n\n", "\n", "###", "##", "#", " ", ""]
        )
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """문서로부터 Vector Store 생성"""
        text_splitter = self._get_text_splitter()
        splits = text_splitter.split_documents(documents)
        
        # 디렉토리 생성
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="contract_knowledge"
        )
        
        return self.vectorstore
    
    def load_vectorstore(self) -> Optional[Chroma]:
        """기존 Vector Store 로드"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="contract_knowledge"
            )
            return self.vectorstore
        return None
    
    def add_documents(self, documents: List[Document]):
        """문서 추가"""
        if self.vectorstore is None:
            self.create_vectorstore(documents)
        else:
            text_splitter = self._get_text_splitter()
            splits = text_splitter.split_documents(documents)
            self.vectorstore.add_documents(splits)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """유사도 검색"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            return []
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def get_retriever(self, k: int = 5):
        """Retriever 반환"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore:
            return self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
        return None


def initialize_knowledge_base():
    """법률 지식 베이스 초기화"""
    data_dir = app_config.data_dir
    raw_dir = os.path.join(data_dir, "raw")
    
    documents = []
    
    # 법률 지식 로드
    legal_file = os.path.join(raw_dir, "legal_knowledge.txt")
    if os.path.exists(legal_file):
        with open(legal_file, 'r', encoding='utf-8') as f:
            content = f.read()
            documents.append(Document(
                page_content=content,
                metadata={"source": "legal_knowledge", "type": "법률조항"}
            ))
    
    # 표준계약서 로드
    standard_file = os.path.join(raw_dir, "standard_contracts.txt")
    if os.path.exists(standard_file):
        with open(standard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            documents.append(Document(
                page_content=content,
                metadata={"source": "standard_contracts", "type": "표준계약서"}
            ))
    
    if documents:
        manager = VectorStoreManager()
        manager.create_vectorstore(documents)
        print(f"✅ 지식 베이스 초기화 완료: {len(documents)}개 문서")
        return manager
    
    print("⚠️ 로드할 문서가 없습니다.")
    return None

