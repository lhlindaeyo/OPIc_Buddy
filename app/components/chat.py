"""
채팅 화면 컴포넌트
"""
import streamlit as st
from utils.speech_utils import display_speech_interface, display_tts_button
from utils.model_loader import generate_response
from components.survey import get_user_profile

def show_chat(gen_pipeline):
    """
    채팅 화면을 표시합니다.
    
    Args:
        gen_pipeline: 로드된 AI 모델 파이프라인
    """
    st.title("🤖 OPIc AI 튜터")
    st.caption("설문조사 결과를 바탕으로 개인 맞춤형 영어 인터뷰를 진행합니다!")

    # 사용자 프로필 표시
    _display_user_profile()

    # 음성 입력 인터페이스
    speech_input = display_speech_interface()
    if speech_input:
        _handle_question(speech_input, gen_pipeline)

    # 텍스트 입력창
    user_input = st.chat_input("💬 메시지를 입력하세요 (영어 또는 한국어)")
    if user_input:
        _handle_question(user_input, gen_pipeline)

    # 대화 렌더링
    _render_chat_history()

def _display_user_profile():
    """사용자 프로필을 간단하게 표시합니다."""
    profile = get_user_profile()
    
    with st.expander("나의 프로필 (설문조사 결과)"):
        st.info(profile)
        
        # 상세 데이터도 보여주기 (개발자용)
        if hasattr(st.session_state, 'survey_data'):
            with st.expander("상세 데이터 (개발자용)"):
                st.json(st.session_state.survey_data)

def _handle_question(question, gen_pipeline):
    """
    사용자 질문을 처리하고 AI 응답을 생성합니다.
    사용자 프로필 정보를 포함한 맞춤형 응답을 생성합니다.
    
    Args:
        question (str): 사용자 질문
        gen_pipeline: AI 모델 파이프라인
    """
    # 사용자 질문을 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # 사용자 프로필 정보를 포함한 컨텍스트 생성
    user_profile = get_user_profile()
    enhanced_prompt = f"""You are an OPIc (Oral Proficiency Interview-computer) English tutor. 

User Profile: {user_profile}

Based on the user's background information above, provide a helpful and encouraging response to their question. Keep your response conversational and supportive for English learning.

User Question: {question}

Response:"""
    
    # 프롬프트 표시 (디버깅용)
    with st.expander("AI 프롬프트 (개발자용)"):
        st.code(enhanced_prompt)
    
    # AI 응답 생성
    answer = generate_response(gen_pipeline, enhanced_prompt)
    
    # AI 응답을 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "bot", "content": answer})

def _render_chat_history():
    """채팅 기록을 렌더링합니다."""
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
            # AI 응답에만 TTS 버튼 추가
            if msg["role"] == "bot":
                display_tts_button(msg["content"])
