"""
ContractGuard AI - 메인 애플리케이션
AI 기반 계약서 리스크 분석 어시스턴트
"""
# 필수 패키지 자동 설치
import subprocess
import sys

def install_package(package):
    """패키지가 없으면 자동 설치"""
    try:
        __import__(package.split('[')[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 필수 패키지 확인 및 설치
try:
    import PyPDF2
except ImportError:
    install_package("PyPDF2")
    import PyPDF2

try:
    import docx
except ImportError:
    install_package("python-docx")
    import docx

import streamlit as st
from typing import Dict, Any
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="ContractGuard AI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """세션 상태 초기화"""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "contract_text" not in st.session_state:
        st.session_state.contract_text = ""


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/contract.png", width=80)
        st.title("ContractGuard AI")
        st.markdown("*AI 기반 계약서 리스크 분석 어시스턴트*")

        st.divider()

        # 파일 업로드
        st.subheader("📄 계약서 업로드")
        uploaded_file = st.file_uploader(
            "PDF, DOCX, TXT 파일을 업로드하세요",
            type=["pdf", "docx", "txt"],
            help="계약서 파일을 업로드하면 AI가 자동으로 분석합니다."
        )

        # 또는 직접 입력
        st.subheader("✏️ 또는 직접 입력")
        manual_input = st.text_area(
            "계약서 내용을 붙여넣기",
            height=150,
            placeholder="계약서 전문을 여기에 붙여넣으세요..."
        )

        st.divider()

        # 분석 시작 버튼
        analyze_button = st.button(
            "🔍 분석 시작",
            type="primary",
            use_container_width=True
        )

        # 초기화 버튼
        if st.button("🔄 새로운 분석", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.chat_history = []
            st.session_state.contract_text = ""
            st.rerun()

        return uploaded_file, manual_input, analyze_button


def process_uploaded_file(uploaded_file) -> str:
    """업로드된 파일 처리"""
    from utils.document_loader import DocumentLoader

    try:
        file_type = uploaded_file.name.split('.')[-1].lower()
        text = DocumentLoader.load(uploaded_file, file_type)
        return text
    except Exception as e:
        st.error(f"파일 처리 오류: {str(e)}")
        return ""


def run_analysis(contract_text: str) -> Dict[str, Any]:
    """계약서 분석 실행"""
    from graph.workflow import ContractAnalysisWorkflow

    workflow = ContractAnalysisWorkflow()
    return workflow.run(contract_text)


def render_risk_score(score: int):
    """리스크 점수 표시"""
    # 색상 결정
    if score <= 30:
        color = "green"
        status = "안전"
    elif score <= 60:
        color = "orange"
        status = "주의"
    else:
        color = "red"
        status = "위험"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
            <h1 style="color: {color}; font-size: 72px; margin: 0;">{score}</h1>
            <p style="color: {color}; font-size: 24px; margin: 5px 0;">/ 100점</p>
            <p style="font-size: 20px; color: {color};">리스크 수준: <strong>{status}</strong></p>
        </div>
        """, unsafe_allow_html=True)



def render_analysis_result(result: Dict[str, Any]):
    """분석 결과 렌더링"""
    if "error" in result:
        st.error(f"분석 오류: {result['error']}")
        return

    summary = result.get("summary", {})

    # 요약 정보
    st.header("📊 분석 결과 요약")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 계약 유형", summary.get("contract_type", "알 수 없음"))
    with col2:
        st.metric("⚠️ 리스크 점수", f"{summary.get('risk_score', 50)}/100")
    with col3:
        risk_level = summary.get("risk_level", "중")
        st.metric("🚦 리스크 수준", risk_level)

    # 리스크 점수 시각화
    st.subheader("🎯 리스크 점수")
    render_risk_score(summary.get("risk_score", 50))

    st.divider()

    # 탭으로 상세 정보 표시
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 리스크 분석", "📑 조항 비교", "💡 개선 제안", "📝 원문 분석"])

    with tab1:
        render_risk_tab(result.get("risks", {}))

    with tab2:
        render_comparison_tab(result.get("comparison", {}))

    with tab3:
        render_improvement_tab(result.get("improvements", {}))

    with tab4:
        render_analysis_tab(result.get("analysis", {}))


def render_risk_tab(risks: Dict[str, Any]):
    """리스크 분석 탭"""
    st.subheader("🚨 식별된 리스크")

    risk_items = risks.get("risks", [])
    if isinstance(risk_items, list) and risk_items:
        for i, risk in enumerate(risk_items, 1):
            severity = risk.get("severity", "중")
            color = {"상": "🔴", "중": "🟡", "하": "🟢"}.get(severity, "🟡")

            with st.expander(f"{color} 리스크 {i}: {risk.get('risk_type', '알 수 없음')}"):
                st.write(f"**조항:** {risk.get('clause', 'N/A')}")
                st.write(f"**설명:** {risk.get('description', 'N/A')}")
                st.write(f"**법적 근거:** {risk.get('legal_basis', 'N/A')}")
    else:
        st.info("식별된 주요 리스크가 없습니다.")

    # 안전한 조항
    safe_clauses = risks.get("safe_clauses", [])
    if safe_clauses:
        st.subheader("✅ 안전한 조항")
        for clause in safe_clauses:
            st.write(f"- {clause}")


def render_comparison_tab(comparison: Dict[str, Any]):
    """조항 비교 탭"""
    st.subheader("📑 표준계약서 비교 결과")

    results = comparison.get("comparison_results", [])
    if isinstance(results, list) and results:
        for item in results:
            status = item.get("status", "")
            icon = {"일치": "✅", "변경": "⚠️", "누락": "❌", "추가": "➕"}.get(status, "📌")
            assessment = item.get("assessment", "중립")

            with st.expander(f"{icon} {item.get('clause_name', '조항')} - {status}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**현재 계약서:**")
                    st.write(item.get("current", "N/A"))
                with col2:
                    st.write("**표준계약서:**")
                    st.write(item.get("standard", "N/A"))
                st.write(f"**평가:** {assessment}")
    else:
        st.info("비교 결과가 없습니다.")

    # 누락 조항
    missing = comparison.get("missing_clauses", [])
    if missing:
        st.warning("⚠️ 누락된 표준 조항")
        for clause in missing:
            st.write(f"- {clause}")


def render_improvement_tab(improvements: Dict[str, Any]):
    """개선 제안 탭"""
    st.subheader("💡 개선 제안사항")

    priority_items = improvements.get("priority_improvements", [])
    if isinstance(priority_items, list) and priority_items:
        for item in priority_items:
            priority = item.get("priority", 3)

            with st.expander(f"우선순위 {priority}: 조항 수정 제안"):
                st.write("**현재 문구:**")
                st.code(item.get("current_clause", "N/A"))
                st.write("**제안 문구:**")
                st.code(item.get("suggested_clause", "N/A"))
                st.write(f"**수정 이유:** {item.get('reason', 'N/A')}")
                st.info(f"💡 협상 팁: {item.get('negotiation_tip', 'N/A')}")

    # 종합 권고
    overall = improvements.get("overall_recommendation", "")
    if overall:
        st.subheader("📋 종합 권고사항")
        st.write(overall)


def render_analysis_tab(analysis: Dict[str, Any]):
    """원문 분석 탭"""
    st.subheader("📝 계약서 분석 상세")

    # 계약 유형
    st.write(f"**계약 유형:** {analysis.get('contract_type', 'N/A')}")

    # 당사자 정보
    parties = analysis.get("parties", {})
    if parties:
        st.write("**계약 당사자:**")
        st.write(f"- 갑: {parties.get('party_a', 'N/A')}")
        st.write(f"- 을: {parties.get('party_b', 'N/A')}")

    # 핵심 조건
    key_terms = analysis.get("key_terms", {})
    if key_terms:
        st.write("**핵심 조건:**")
        st.write(f"- 계약금액: {key_terms.get('amount', 'N/A')}")
        st.write(f"- 계약기간: {key_terms.get('period', 'N/A')}")
        st.write(f"- 계약대상: {key_terms.get('subject', 'N/A')}")

    # 조항 요약
    clauses = analysis.get("clauses_summary", [])
    if clauses:
        st.write("**조항 요약:**")
        for clause in clauses:
            st.write(f"- **{clause.get('title', '')}**: {clause.get('summary', '')}")


def render_chat_interface():
    """대화형 상담 인터페이스"""
    st.header("💬 AI 상담")
    st.write("분석 결과에 대해 추가로 궁금한 점을 질문하세요.")

    # 채팅 히스토리 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 사용자 입력
    user_input = st.chat_input("질문을 입력하세요...")

    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # AI 응답 생성
        with st.spinner("답변을 생성중입니다..."):
            response = generate_chat_response(user_input)

        # AI 응답 추가
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()


def generate_chat_response(user_question: str) -> str:
    """채팅 응답 생성"""
    from langchain_openai import AzureChatOpenAI
    from langchain.schema import HumanMessage
    from config.settings import azure_config
    from prompts.templates import PromptTemplates
    from rag.retriever import ContractRetriever

    try:
        llm = AzureChatOpenAI(
            azure_endpoint=azure_config.endpoint,
            api_key=azure_config.api_key,
            api_version=azure_config.api_version,
            azure_deployment=azure_config.gpt4o_mini,
            temperature=0.3
        )

        # 분석 결과 요약
        analysis_summary = ""
        if st.session_state.analysis_result:
            summary = st.session_state.analysis_result.get("summary", {})
            analysis_summary = f"계약유형: {summary.get('contract_type', 'N/A')}, 리스크점수: {summary.get('risk_score', 'N/A')}"

        # RAG 컨텍스트
        retriever = ContractRetriever()
        context = retriever.get_context_for_analysis(user_question, "general")

        prompt = PromptTemplates.CONSULTATION.format(
            analysis_summary=analysis_summary,
            user_question=user_question,
            context=context
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


def main():
    """메인 함수"""
    initialize_session_state()

    # 사이드바
    uploaded_file, manual_input, analyze_button = render_sidebar()

    # 메인 영역
    st.title("📋 ContractGuard AI")
    st.markdown("### AI 기반 계약서 리스크 분석 어시스턴트")
    st.markdown("---")

    # 분석 실행
    if analyze_button:
        contract_text = ""

        if uploaded_file:
            contract_text = process_uploaded_file(uploaded_file)
        elif manual_input:
            contract_text = manual_input

        if contract_text:
            st.session_state.contract_text = contract_text

            with st.spinner("🔍 계약서를 분석중입니다... (약 1-2분 소요)"):
                result = run_analysis(contract_text)
                st.session_state.analysis_result = result

            st.success("✅ 분석이 완료되었습니다!")
            st.rerun()
        else:
            st.warning("⚠️ 계약서를 업로드하거나 내용을 입력해주세요.")

    # 결과 표시
    if st.session_state.analysis_result:
        render_analysis_result(st.session_state.analysis_result)
        st.divider()
        render_chat_interface()
    else:
        # 안내 메시지
        st.info("""
        👋 **ContractGuard AI**에 오신 것을 환영합니다!

        이 서비스는 AI를 활용하여 계약서의 잠재적 리스크를 분석하고 개선안을 제시합니다.

        **사용 방법:**
        1. 왼쪽 사이드바에서 계약서 파일을 업로드하거나 내용을 직접 입력하세요
        2. '분석 시작' 버튼을 클릭하세요
        3. AI가 계약서를 분석하고 결과를 보여드립니다
        4. 추가 질문이 있으면 채팅으로 상담하세요

        **분석 항목:**
        - 📊 리스크 점수 및 수준 평가
        - 🚨 주요 리스크 조항 식별
        - 📑 표준계약서와 비교
        - 💡 구체적인 개선 제안
        """)

        # 샘플 계약서
        with st.expander("📝 샘플 계약서로 테스트하기"):
            sample_contract = """
용역계약서

제1조 (목적)
"갑"은 "을"에게 소프트웨어 개발 용역을 위탁하고, "을"은 이를 성실히 수행한다.

제2조 (용역 내용)
1. 프로젝트명: AI 챗봇 시스템 개발
2. 개발 범위: 요구사항 분석, 설계, 개발, 테스트

제3조 (계약 금액)
1. 총 용역대금은 금 오천만원(₩50,000,000)으로 한다.
2. 대금 지급: 착수금 30%, 중도금 30%, 잔금 40%

제4조 (계약 기간)
계약기간은 2024년 1월 1일부터 2024년 6월 30일까지로 한다.

제5조 (손해배상)
"을"이 본 계약을 위반하여 "갑"에게 손해를 입힌 경우, 직접손해, 간접손해, 특별손해를 포함한 모든 손해를 배상한다. 손해배상의 한도는 없다.

제6조 (비밀유지)
쌍방은 본 계약과 관련하여 알게 된 상대방의 비밀정보를 10년간 유지하여야 한다.

제7조 (계약해지)
"갑"은 사전 통지 없이 언제든지 본 계약을 해지할 수 있다.

제8조 (지식재산권)
본 계약에 따른 모든 성과물과 "을"의 기존 기술을 포함한 모든 지식재산권은 "갑"에게 귀속된다.
            """
            st.text_area("샘플 계약서", sample_contract, height=400)
            st.info("위 내용을 복사하여 왼쪽 사이드바의 '직접 입력' 창에 붙여넣고 분석해보세요!")


if __name__ == "__main__":
    main()
