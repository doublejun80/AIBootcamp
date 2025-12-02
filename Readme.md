# 📋 ContractGuard AI

## AI 기반 계약서 리스크 분석 어시스턴트

ContractGuard AI는 LangGraph Multi-Agent 시스템과 RAG를 활용하여 계약서의 잠재적 리스크를 분석하고 개선안을 제시하는 AI 어시스턴트입니다.

---

## 🎯 주요 기능

| 기능 | 설명 |
|------|------|
| **계약서 분석** | PDF, DOCX, TXT 형식의 계약서 자동 분석 |
| **리스크 평가** | 0-100점 리스크 점수 및 상세 리스크 식별 |
| **표준계약서 비교** | 표준 템플릿과 비교하여 누락/변경 조항 확인 |
| **개선안 제안** | 구체적인 수정 문구 및 협상 전략 제시 |
| **대화형 상담** | 분석 결과에 대한 추가 질문 가능 |

---

## 🏗️ 기술 스택

- **Frontend**: Streamlit
- **LLM**: Azure OpenAI (GPT-4o-mini)
- **Agent Framework**: LangChain, LangGraph
- **Vector DB**: ChromaDB
- **Embedding**: text-embedding-3-large

---

## 📁 프로젝트 구조

```
project/
├── app.py                 # Streamlit 메인 앱
├── requirements.txt       # 의존성
├── config/
│   └── settings.py        # 설정 관리
├── agents/                # Multi-Agent
│   ├── contract_analyzer.py
│   ├── risk_evaluator.py
│   ├── clause_comparator.py
│   └── improvement_advisor.py
├── graph/
│   └── workflow.py        # LangGraph 워크플로우
├── rag/
│   ├── vectorstore.py     # Vector DB
│   └── retriever.py       # 검색 로직
├── prompts/
│   └── templates.py       # 프롬프트 템플릿
├── utils/
│   ├── document_loader.py # 문서 로더
│   └── text_processor.py  # 텍스트 처리
└── data/
    └── raw/               # 법률 지식 데이터
```

---

## 🚀 실행 방법

### 1. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env
# API 키 설정
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 지식베이스 초기화 (최초 1회)
```bash
python -c "from rag.vectorstore import initialize_knowledge_base; initialize_knowledge_base()"
```

### 4. 앱 실행
```bash
streamlit run app.py
```

---

## 📊 평가 기준 충족

| 평가 요소 | 구현 내용 |
|----------|----------|
| **Prompt Engineering** | 역할부여, Chain-of-Thought, Few-shot 적용 |
| **LangChain/LangGraph** | 4개 Agent 협업 워크플로우 |
| **RAG** | ChromaDB + 법률 지식 검색 |
| **Streamlit** | 파일 업로드, 대시보드, 채팅 UI |
| **Memory** | 대화 히스토리 유지 |

---

## 👤 개발자
AI Bootcamp 과제
