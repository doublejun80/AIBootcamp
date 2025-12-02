"""
ContractGuard AI - 설정 관리 모듈
환경변수 로드 및 애플리케이션 설정 관리
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# 환경변수 로드
load_dotenv()


class AzureOpenAIConfig(BaseModel):
    """Azure OpenAI 설정"""
    endpoint: str = os.getenv("AOAI_ENDPOINT", "")
    api_key: str = os.getenv("AOAI_API_KEY", "")
    api_version: str = "2024-02-15-preview"
    
    # 배포 모델명
    gpt4o_mini: str = os.getenv("AOAI_DEPLOY_GPT4O_MINI", "gpt-4o-mini")
    gpt4o: str = os.getenv("AOAI_DEPLOY_GPT4O", "gpt-4o")
    embed_large: str = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE", "text-embedding-3-large")
    embed_small: str = os.getenv("AOAI_DEPLOY_EMBED_3_SMALL", "text-embedding-3-small")


class AppConfig(BaseModel):
    """애플리케이션 설정"""
    app_name: str = "ContractGuard AI"
    app_description: str = "AI 기반 계약서 리스크 분석 어시스턴트"
    version: str = "1.0.0"
    
    # RAG 설정
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retriever_k: int = 5
    
    # 경로 설정
    data_dir: str = "data"
    vectorstore_dir: str = "data/vectorstore"


# 전역 설정 인스턴스
azure_config = AzureOpenAIConfig()
app_config = AppConfig()


def validate_config() -> bool:
    """설정 유효성 검사"""
    if not azure_config.endpoint:
        raise ValueError("AOAI_ENDPOINT 환경변수가 설정되지 않았습니다.")
    if not azure_config.api_key:
        raise ValueError("AOAI_API_KEY 환경변수가 설정되지 않았습니다.")
    return True

