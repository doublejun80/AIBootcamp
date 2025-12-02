"""
ContractGuard AI - LangGraph 워크플로우
Multi-Agent 협업 오케스트레이션
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.contract_analyzer import ContractAnalyzerAgent
from agents.risk_evaluator import RiskEvaluatorAgent
from agents.clause_comparator import ClauseComparatorAgent
from agents.improvement_advisor import ImprovementAdvisorAgent


class ContractAnalysisState(TypedDict):
    """워크플로우 상태 정의"""
    contract_text: str
    analysis_result: Dict[str, Any]
    risk_result: Dict[str, Any]
    comparison_result: Dict[str, Any]
    improvement_result: Dict[str, Any]
    final_report: Dict[str, Any]
    current_step: str
    error: str


class ContractAnalysisWorkflow:
    """계약서 분석 워크플로우"""
    
    def __init__(self):
        # Agent 초기화
        self.contract_analyzer = ContractAnalyzerAgent()
        self.risk_evaluator = RiskEvaluatorAgent()
        self.clause_comparator = ClauseComparatorAgent()
        self.improvement_advisor = ImprovementAdvisorAgent()
        
        # 그래프 생성
        self.graph = self._build_graph()
        
        # 메모리 (멀티턴 대화용)
        self.memory = MemorySaver()
    
    def _build_graph(self) -> StateGraph:
        """워크플로우 그래프 구성"""
        workflow = StateGraph(ContractAnalysisState)
        
        # 노드 추가
        workflow.add_node("analyze", self._analyze_contract)
        workflow.add_node("evaluate_risk", self._evaluate_risk)
        workflow.add_node("compare_clauses", self._compare_clauses)
        workflow.add_node("suggest_improvements", self._suggest_improvements)
        workflow.add_node("generate_report", self._generate_report)
        
        # 엣지 연결 (순차 실행)
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "evaluate_risk")
        workflow.add_edge("evaluate_risk", "compare_clauses")
        workflow.add_edge("compare_clauses", "suggest_improvements")
        workflow.add_edge("suggest_improvements", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _analyze_contract(self, state: ContractAnalysisState) -> Dict[str, Any]:
        """1단계: 계약서 분석"""
        result = self.contract_analyzer.invoke({
            "contract_text": state["contract_text"]
        })
        return {
            "analysis_result": result,
            "current_step": "analyze"
        }
    
    def _evaluate_risk(self, state: ContractAnalysisState) -> Dict[str, Any]:
        """2단계: 리스크 평가"""
        result = self.risk_evaluator.invoke({
            "contract_text": state["contract_text"],
            "analysis_result": state["analysis_result"]
        })
        return {
            "risk_result": result,
            "current_step": "evaluate_risk"
        }
    
    def _compare_clauses(self, state: ContractAnalysisState) -> Dict[str, Any]:
        """3단계: 조항 비교"""
        contract_type = state["analysis_result"].get("contract_type", "일반계약")
        result = self.clause_comparator.invoke({
            "contract_text": state["contract_text"],
            "contract_type": contract_type
        })
        return {
            "comparison_result": result,
            "current_step": "compare_clauses"
        }
    
    def _suggest_improvements(self, state: ContractAnalysisState) -> Dict[str, Any]:
        """4단계: 개선 제안"""
        result = self.improvement_advisor.invoke({
            "risk_result": state["risk_result"],
            "comparison_result": state["comparison_result"]
        })
        return {
            "improvement_result": result,
            "current_step": "suggest_improvements"
        }
    
    def _generate_report(self, state: ContractAnalysisState) -> Dict[str, Any]:
        """5단계: 최종 리포트 생성"""
        report = {
            "summary": {
                "contract_type": state["analysis_result"].get("contract_type", "알 수 없음"),
                "risk_score": state["risk_result"].get("risk_score", 50),
                "risk_level": state["risk_result"].get("risk_level", "중")
            },
            "analysis": state["analysis_result"],
            "risks": state["risk_result"],
            "comparison": state["comparison_result"],
            "improvements": state["improvement_result"]
        }
        return {
            "final_report": report,
            "current_step": "complete"
        }
    
    def run(self, contract_text: str, thread_id: str = "default") -> Dict[str, Any]:
        """워크플로우 실행"""
        initial_state = {
            "contract_text": contract_text,
            "analysis_result": {},
            "risk_result": {},
            "comparison_result": {},
            "improvement_result": {},
            "final_report": {},
            "current_step": "start",
            "error": ""
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = self.graph.invoke(initial_state, config)
            return result["final_report"]
        except Exception as e:
            return {"error": str(e)}

