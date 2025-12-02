"""
ContractGuard AI - 텍스트 전처리 모듈
계약서 텍스트 정제 및 구조화
"""
import re
from typing import List, Dict


class TextProcessor:
    """텍스트 전처리기"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트 정제"""
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 줄바꿈 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 앞뒤 공백 제거
        text = text.strip()
        return text
    
    @staticmethod
    def extract_clauses(text: str) -> List[Dict[str, str]]:
        """계약서에서 조항 추출"""
        clauses = []
        
        # 조/항 패턴 매칭 (예: 제1조, 제2조, 1., 2. 등)
        patterns = [
            r'제\s*(\d+)\s*조[^\n]*',  # 제N조
            r'(\d+)\.\s*[가-힣]',       # N. 한글
            r'[①②③④⑤⑥⑦⑧⑨⑩]',      # 원숫자
        ]
        
        # 제N조 패턴으로 분할
        article_pattern = r'(제\s*\d+\s*조[^\n]*)'
        parts = re.split(article_pattern, text)
        
        current_title = ""
        current_content = ""
        
        for i, part in enumerate(parts):
            if re.match(r'제\s*\d+\s*조', part):
                if current_title:
                    clauses.append({
                        "title": current_title.strip(),
                        "content": current_content.strip()
                    })
                current_title = part
                current_content = ""
            else:
                current_content += part
        
        # 마지막 조항 추가
        if current_title:
            clauses.append({
                "title": current_title.strip(),
                "content": current_content.strip()
            })
        
        return clauses
    
    @staticmethod
    def identify_contract_type(text: str) -> str:
        """계약서 유형 식별"""
        text_lower = text.lower()
        
        type_keywords = {
            "용역계약": ["용역", "서비스 제공", "업무 수행"],
            "임대차계약": ["임대", "임차", "보증금", "월세", "전세"],
            "비밀유지계약(NDA)": ["비밀유지", "기밀", "confidential", "nda"],
            "근로계약": ["근로", "급여", "연봉", "고용"],
            "매매계약": ["매매", "매도", "매수", "대금"],
            "도급계약": ["도급", "시공", "공사"],
            "라이선스계약": ["라이선스", "license", "사용권", "저작권"],
            "투자계약": ["투자", "지분", "주식", "출자"],
        }
        
        for contract_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return contract_type
        
        return "일반계약"
    
    @staticmethod
    def count_tokens_approx(text: str) -> int:
        """토큰 수 대략적 계산 (한글 기준)"""
        # 한글은 대략 글자당 2-3 토큰
        korean_chars = len(re.findall(r'[가-힣]', text))
        other_chars = len(text) - korean_chars
        return int(korean_chars * 2.5 + other_chars * 0.25)

