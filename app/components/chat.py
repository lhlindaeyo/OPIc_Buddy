"""
채팅 화면 컴포넌트
"""
import streamlit as st
from utils.speech_utils import display_speech_interface, display_tts_button
from utils.model_loader import generate_response
from components.survey import get_user_profile

def show_chat(model_interface):
    """
    채팅 화면을 표시합니다.
    
    Args:
        model_interface: 로드된 AI 모델 인터페이스 (로컬/API/RAG 지원)
    """
    st.title("🤖 OPIc AI 튜터")
    
    # 모델 타입에 따른 캡션 표시
    model_type = model_interface.get("type", "unknown") if model_interface else "unknown"
    if model_type == "rag":
        st.caption("🔍 RAG + Phi-1.5 모델로 OPIc 전문 데이터베이스를 활용한 맞춤형 영어 튜터링을 제공합니다!")
        st.success(f"✅ **RAG 시스템 활성화**: {model_interface.get('model_name', 'Phi-1.5 + E5')}")
    elif model_type == "local":
        st.caption("설문조사 결과를 바탕으로 개인 맞춤형 영어 인터뷰를 진행합니다!")
    else:
        st.caption("AI 튜터와 함께 영어 연습을 시작해보세요!")

    # 사용자 프로필 표시
    _display_user_profile()

    # 음성 입력 인터페이스
    display_speech_interface()
    
    # 음성 입력이 있을 경우 처리
    if "user_input" in st.session_state and st.session_state.user_input:
        _handle_question(st.session_state.user_input, model_interface)
        # 처리 후 초기화
        st.session_state.user_input = ""

    # 텍스트 입력창
    user_input = st.chat_input("💬 메시지를 입력하세요 (영어 또는 한국어)")
    if user_input:
        _handle_question(user_input, model_interface)

    # 대화 렌더링
    _render_chat_history()

def _display_user_profile():
    """사용자 프로필을 간단하게 표시합니다."""
    profile = get_user_profile()
    
    with st.expander("나의 프로필 (설문조사 결과)"):
        st.info(profile)
        
        # Survey Value Pool 표시 (개발자용)
        with st.expander("🛠️ Survey Value Pool (Dev)"):
            survey_value_pool = st.session_state.get("survey_value_pool", [])
            if survey_value_pool:
                pool_text = "[\n"
                for i, value in enumerate(survey_value_pool):
                    pool_text += f'  {i}: "{value}"\n'
                pool_text += "]"
                st.code(pool_text)
            else:
                st.code("[]")
        
        # 상세 데이터도 보여주기 (개발자용)
        if hasattr(st.session_state, 'survey_data'):
            with st.expander("🔍 상세 데이터 (개발자용)", expanded=False):
                survey_data = st.session_state.survey_data
                if survey_data:
                    import json
                    st.code(json.dumps(survey_data, indent=2, ensure_ascii=False), language="json")
                else:
                    st.info("설문조사 데이터가 없습니다.")

def _handle_question(question, model_interface):
    """
    사용자 질문을 처리하고 AI 응답을 생성합니다.
    사용자 프로필 정보를 포함한 맞춤형 응답을 생성합니다.
    
    Args:
        question (str): 사용자 질문
        model_interface: AI 모델 인터페이스 (로컬/API/RAG 지원)
    """
    # 사용자 질문을 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # 사용자 프로필 정보를 포함한 컨텍스트 생성
    user_profile = get_user_profile()
    
    # 모델 타입에 따른 프롬프트 생성
    model_type = model_interface.get("type", "local") if model_interface else "local"
    
    if model_type == "rag":
        # RAG 모델용 간단한 프롬프트 (RAG 시스템이 컨텍스트를 자동으로 찾아줌)
        enhanced_prompt = f"""As an OPIc English tutor, help with this question.

User Profile: {user_profile}

Question: {question}"""
    else:
        # 기존 로컬 모델용 상세한 프롬프트
        enhanced_prompt = f"""You are an OPIc (Oral Proficiency Interview-computer) English tutor. 

User Profile: {user_profile}

Based on the user's background information above, provide a helpful and encouraging response to their question. Keep your response conversational and supportive for English learning.

User Question: {question}

Response:"""
    
    # 프롬프트 표시 (디버깅용)
    with st.expander("AI 프롬프트 (개발자용)"):
        st.code(enhanced_prompt)
        if model_interface:
            st.info(f"**사용 모델**: {model_type.upper()} - {model_interface.get('model_name', 'Unknown')}")
    
    # AI 응답 생성
    with st.spinner("🤖 AI가 생각 중입니다..."):
        answer = generate_response(model_interface, enhanced_prompt)
        
        # 빈 응답일 경우 기본 응답 제공
        if not answer or answer.strip() in ["", "❌ 모델이 로드되지 않았습니다."]:
            answer = f"안녕하세요! 질문해주신 '{question}'에 대해 답변드리겠습니다. OPIc 준비를 도와드릴게요! 더 구체적인 질문이 있으시면 언제든 말씀해주세요."
    
    # AI 응답을 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "bot", "content": answer})

def _render_chat_history():
    """채팅 기록을 렌더링합니다."""
    for idx, msg in enumerate(st.session_state.chat_history):
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
            # AI 응답에만 TTS 버튼 추가
            if msg["role"] == "bot":
                display_tts_button(msg["content"], message_index=idx)
