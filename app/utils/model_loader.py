"""
AI 모델 인터페이스 - 로컬/API/RAG 모두 지원
"""
import streamlit as st
import os
import sys
from typing import Optional
from pathlib import Path

# 환경 변수로 모델 타입 설정
MODEL_TYPE = os.getenv("MODEL_TYPE", "rag")  # "local", "api", "rag"
API_KEY = os.getenv("OPENAI_API_KEY", "")

# RAG 관련 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

def load_model():
    """
    모델을 로드합니다. 
    로컬 모델, API, 또는 RAG 설정에 따라 적절한 인터페이스를 반환합니다.
    """
    if MODEL_TYPE == "api":
        return _load_api_client()
    elif MODEL_TYPE == "rag":
        return _load_rag_model()
    else:
        return _load_local_model()

@st.cache_resource
def _load_rag_model():
    """RAG + Phi 모델을 로드합니다."""
    try:
        # RAG 모듈 동적 임포트 (캐시된 리소스에서)
        from rag.rag import run_rag
        
        return {
            "type": "rag",
            "rag_function": run_rag,
            "model_name": "Phi-1.5 + E5 Embeddings"
        }
    except Exception as e:
        st.error(f"RAG 모델 로딩 중 오류: {e}")
        # Fallback to local model
        st.warning("RAG 모델을 사용할 수 없어 로컬 모델로 전환합니다.")
        return _load_local_model()

@st.cache_resource
def _load_local_model():
    """로컬 FLAN-T5 모델을 로드합니다."""
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
        return {
            "type": "local",
            "pipeline": pipeline("text2text-generation", model=model, tokenizer=tokenizer)
        }
    except Exception as e:
        st.error(f"로컬 모델 로딩 중 오류: {e}")
        return None

def _load_api_client():
    """API 클라이언트를 설정합니다. (향후 OpenAI/다른 API 연동용)"""
    return {
        "type": "api",
        "api_key": API_KEY,
        "model": "gpt-3.5-turbo"  # 나중에 사용할 모델
    }

def generate_response(model_interface: Optional[dict], prompt: str, max_tokens: int = 150) -> str:
    """
    통합 응답 생성 함수 - 로컬/API/RAG 모두 지원
    
    Args:
        model_interface: 모델 인터페이스 (로컬 파이프라인, API 설정, 또는 RAG 함수)
        prompt: 완성된 프롬프트
        max_tokens: 최대 토큰 수
    
    Returns:
        생성된 응답
    """
    if model_interface is None:
        return "❌ 모델이 로드되지 않았습니다."
    
    if model_interface["type"] == "api":
        return _generate_api_response(model_interface, prompt, max_tokens)
    elif model_interface["type"] == "rag":
        return _generate_rag_response(model_interface, prompt, max_tokens)
    else:
        return _generate_local_response(model_interface, prompt, max_tokens)

def _generate_rag_response(model_interface: dict, prompt: str, max_tokens: int) -> str:
    """RAG 모델로 응답 생성"""
    try:
        rag_function = model_interface["rag_function"]
        
        # 사용자 질문 추출 (프롬프트에서 실제 질문 부분만 추출)
        user_question = prompt
        if "User Question:" in prompt:
            user_question = prompt.split("User Question:")[-1].strip()
        elif "Question:" in prompt:
            user_question = prompt.split("Question:")[-1].strip()
        
        # RAG 시스템으로 응답 생성 (k=3개의 관련 문서 검색)
        response = rag_function(user_question, k=3)
        
        # 응답 정제
        if not response or len(response.strip()) < 10:
            return "I'm here to help you practice English for OPIc! Could you please ask me something about English conversation or OPIc preparation?"
        
        return response.strip()
        
    except Exception as e:
        st.error(f"RAG 모델 오류: {e}")
        return f"I apologize for the technical issue. Could you please try asking your question again? (Error: {str(e)[:50]})"

def _generate_local_response(model_interface: dict, prompt: str, max_tokens: int) -> str:
    """로컬 모델로 응답 생성"""
    try:
        pipeline_model = model_interface["pipeline"]
        
        # 더 간단한 프롬프트로 변경
        simple_prompt = f"Question: {prompt.split('User Question:')[-1].replace('Response:', '').strip()}\nAnswer:"
        
        response = pipeline_model(
            simple_prompt, 
            max_new_tokens=max_tokens, 
            do_sample=True, 
            temperature=0.7,
            repetition_penalty=1.2,  # 반복 방지
            num_beams=2
        )
        
        answer = response[0]["generated_text"].replace(simple_prompt, "").strip()
        
        # 너무 짧거나 반복되는 답변 필터링
        if not answer or len(answer) < 10 or answer.count(answer.split()[0] if answer.split() else "") > 3:
            return "Hello! I'm here to help you practice English for OPIc. Could you please ask me something specific about English conversation or OPIc preparation?"
        
        return answer
    except Exception as e:
        return f"I'm sorry, I had a technical issue. Could you please try asking your question again? (Error: {str(e)[:50]})"

def _generate_api_response(model_interface: dict, prompt: str, max_tokens: int) -> str:
    """API로 응답 생성 (향후 구현 예정)"""
    # TODO: OpenAI API 또는 다른 API 연동
    return "🚧 API 모드는 아직 구현 중입니다. 현재는 로컬 모델을 사용해주세요."
