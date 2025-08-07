"""
채팅 화면 컴포넌트
"""
import streamlit as st
from utils.speech_utils import display_speech_interface, display_tts_button
from utils.model_loader import generate_response
from utils.opic_test_generator import OPIcTestGenerator
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
        st.success("✅ **RAG 질문 개선 시스템 활성화**: 기존 질문을 사용자 관심사에 맞게 개선합니다.")
    elif model_type == "local":
        st.caption("설문조사 결과를 바탕으로 개인 맞춤형 영어 인터뷰를 진행합니다!")
    else:
        st.caption("AI 튜터와 함께 영어 연습을 시작해보세요!")

    # OPIc 시험 시작 버튼 표시
    _display_opic_test_interface(model_interface)

    # 사용자 프로필 표시
    _display_user_profile()

    # 음성 입력 인터페이스
    display_speech_interface()
    
    # 음성 입력이 있을 경우 처리
    if "user_input" in st.session_state and st.session_state.user_input:
        if st.session_state.get("opic_test_active", False):
            _handle_opic_test_answer(st.session_state.user_input, model_interface)
        else:
            _handle_question(st.session_state.user_input, model_interface)
        # 처리 후 초기화
        st.session_state.user_input = ""

    # 텍스트 입력창
    if st.session_state.get("opic_test_active", False):
        # OPIc 시험 모드
        user_input = st.chat_input("💬 답변을 입력하세요 (영어로)")
        if user_input:
            _handle_opic_test_answer(user_input, model_interface)
    else:
        # 일반 채팅 모드
        user_input = st.chat_input("💬 메시지를 입력하세요 (영어 또는 한국어)")
        if user_input:
            _handle_question(user_input, model_interface)

    # 대화 렌더링
    _render_chat_history()

def _display_opic_test_interface(model_interface):
    """OPIc 시험 인터페이스를 표시합니다."""
    survey_value_pool = st.session_state.get("survey_value_pool", [])
    
    if not survey_value_pool:
        st.warning("⚠️ 설문조사를 먼저 완료해주세요.")
        return
    
    # OPIc 시험 상태 초기화
    if "opic_test_generator" not in st.session_state:
        st.session_state.opic_test_generator = OPIcTestGenerator()
        st.session_state.opic_test_active = False
    
    # 현재 상태에 따른 UI 표시
    if not st.session_state.get("opic_test_active", False):
        # 시험 시작 전
        st.markdown("---")
        st.markdown("### 🎯 OPIc 모의고사")
        
        st.info("📋 설문조사 결과를 바탕으로 맞춤형 OPIc 15문항이 생성됩니다.")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown("**시험 구성:**")
            st.markdown("- **1번**: 자기소개")
            st.markdown("- **2-4번**: 기본 세트 (설문 기반)")
            st.markdown("- **5-7번**: 돌발 세트")
        
        with col2:
            st.markdown("")  # 여백
            st.markdown("")  # 여백
            if st.button("🚀 OPIc 모의고사 시작", type="primary"):
                # 시험 초기화 및 시작
                st.session_state.opic_test_generator.initialize_test(survey_value_pool)
                st.session_state.opic_test_active = True
                
                # 첫 번째 질문 자동 생성 (RAG 사용)
                first_question = st.session_state.opic_test_generator.get_current_question()
                if first_question:
                    # 첫 번째 질문은 고정 자기소개이므로 RAG 사용하지 않음
                    if first_question.get("type") == "intro":
                        _add_opic_question_to_chat(first_question)
                    else:
                        # RAG로 질문 생성
                        rag_question = _generate_rag_question(first_question, model_interface)
                        if rag_question:
                            first_question["question"] = rag_question
                        _add_opic_question_to_chat(first_question)
                
                st.rerun()
        
        with col3:
            st.markdown("**추가 구성:**")
            st.markdown("- **8-10번**: 심화 세트 (설문 기반)")
            st.markdown("- **11-13번**: 롤플레잉 세트")
            st.markdown("- **14-15번**: 사회 이슈 세트")
    else:
        # 시험 진행 중 - 진행상황 표시
        progress = st.session_state.opic_test_generator.get_progress()
        current_q, total_q = progress
        
        # 진행 바
        progress_percent = (current_q - 1) / total_q * 100
        st.markdown("---")
        st.markdown(f"### 🎯 OPIc 모의고사 진행 중: {current_q-1}/{total_q}")
        st.progress(progress_percent / 100)
        
        # 시험 종료 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("🛑 시험 종료", type="secondary"):
                st.session_state.opic_test_active = False
                st.session_state.chat_history.append({
                    "role": "bot", 
                    "content": "🏁 **OPIc 모의고사가 종료되었습니다.** 수고하셨습니다!"
                })
                st.rerun()

def _add_opic_question_to_chat(question_data):
    """OPIc 질문을 채팅에 추가합니다."""
    question_type_desc = st.session_state.opic_test_generator.get_question_type_description(question_data["type"])
    
    message = f"""🎤 **Question {question_data['number']}/15**
{question_type_desc}

{question_data['question']}

*Please answer in English.*"""
    
    st.session_state.chat_history.append({
        "role": "bot",
        "content": message
    })

def _handle_opic_test_answer(answer, model_interface):
    """OPIc 시험 답변을 처리합니다."""
    # 사용자 답변을 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "user", "content": answer})
    
    # 답변에 대한 간단한 피드백 (선택적)
    feedback = _generate_simple_feedback(answer)
    if feedback:
        st.session_state.chat_history.append({"role": "bot", "content": feedback})
    
    # 다음 질문으로 이동
    next_question = st.session_state.opic_test_generator.get_next_question()
    
    if next_question:
        # RAG 시스템을 사용하여 Survey Value Pool 기반 질문 생성
        rag_generated_question = _generate_rag_question(next_question, model_interface)
        if rag_generated_question:
            next_question["question"] = rag_generated_question
        
        # 다음 질문 추가
        _add_opic_question_to_chat(next_question)
    else:
        # 시험 완료
        st.session_state.opic_test_active = False
        completion_message = """🎉 **축하합니다! OPIc 모의고사를 완료하셨습니다!**

총 15문항을 모두 완료하셨습니다. 수고하셨습니다!

🔍 **시험 결과 요약:**
- 자기소개: 완료 
- 기본 세트 (설문 기반): 완료 
- 돌발 세트: 완료 
- 심화 세트 (설문 기반): 완료 
- 롤플레잉 세트: 완료 
- 사회 이슈 세트: 완료 

계속 연습하고 싶으시면 다시 시작 버튼을 눌러주세요!"""
        
        st.session_state.chat_history.append({
            "role": "bot",
            "content": completion_message
        })

def _generate_rag_question(question_data, model_interface):
    """RAG 시스템을 사용하여 Survey Value Pool 기반 맞춤형 질문 생성"""
    # 간단한 RAG 기반 질문 개선 시스템
    if not model_interface or model_interface.get("type") != "rag":
        return None
    
    survey_value_pool = st.session_state.get("survey_value_pool", [])
    if not survey_value_pool:
        return None
    
    # 기존 질문을 RAG로 개선
    original_question = question_data.get("question", "")
    survey_context = ", ".join([item for item in survey_value_pool if not item.startswith("level_")])
    
    # 간단한 프롬프트로 질문 개선
    simple_prompt = f"""Improve this OPIc question to be more personalized based on the user's interests:

Original: {original_question}
User interests: {survey_context}

Improved question:"""
    
    try:
        from utils.model_loader import generate_response
        improved_question = generate_response(model_interface, simple_prompt, max_tokens=80)
        
        if improved_question and len(improved_question.strip()) > 10:
            # 간단한 정제
            cleaned = improved_question.strip()
            # 첫 번째 줄만 사용
            if '\n' in cleaned:
                cleaned = cleaned.split('\n')[0]
            # "Improved question:" 제거
            if "Improved question:" in cleaned:
                cleaned = cleaned.split("Improved question:")[-1].strip()
            if "Question:" in cleaned:
                cleaned = cleaned.split("Question:")[-1].strip()
            
            # 원래 질문과 너무 유사하면 None 반환
            if cleaned.lower() != original_question.lower() and len(cleaned) > 20:
                return cleaned
            
    except Exception as e:
        st.error(f"RAG 질문 개선 오류: {e}")
    
    return None
    
    survey_value_pool = st.session_state.get("survey_value_pool", [])
    if not survey_value_pool:
        return None
    
    # Survey Value Pool을 문맥으로 변환
    survey_context = ", ".join(survey_value_pool)
    
    # 질문 타입에 따른 RAG 프롬프트 생성
    question_type = question_data.get("type", "")
    question_number = question_data.get("number", 0)
    
    rag_prompts = {
        "survey_basic": f"""Based on the user's survey data: {survey_context}

Generate an OPIc-style basic question (Question {question_number}/15) that specifically relates to their interests and background. 

The question should be:
- Conversational and natural
- Appropriate for intermediate English learners
- Directly related to their survey responses
- Encourage detailed personal responses

Question:""",

        "unexpected": f"""Generate an OPIc-style unexpected question (Question {question_number}/15) for an intermediate English learner.

The question should be:
- About general topics (not directly related to their survey: {survey_context})
- Conversational and engaging
- Appropriate difficulty for intermediate level
- Encourage personal opinions or experiences

Question:""",

        "survey_advanced": f"""Based on the user's detailed survey data: {survey_context}

Generate an advanced OPIc-style question (Question {question_number}/15) that explores deeper aspects of their interests.

The question should:
- Be more analytical and thoughtful
- Ask about changes, comparisons, or personal growth
- Relate to their specific interests from the survey
- Require explanation and reasoning

Question:""",

        "roleplay": f"""Generate an OPIc-style roleplay question (Question {question_number}/15) for an intermediate English learner.

The question should:
- Present a practical situation they might encounter
- Be appropriate for their level (not too complex)
- Allow them to demonstrate conversational English
- Be relevant to daily life situations

Situation:""",

        "social_issues": f"""Generate an OPIc-style social issues question (Question {question_number}/15) for an intermediate English learner.

The question should:
- Address current social or cultural topics
- Be appropriate for intermediate level (not too academic)  
- Encourage personal opinions and experiences
- Allow for different perspectives

Question:"""
    }
    
    # 기본 타입 추출
    base_type = question_type.split('_')[0] + '_' + question_type.split('_')[1] if '_' in question_type else question_type
    
    # 해당하는 프롬프트 선택
    prompt = rag_prompts.get(base_type, rag_prompts.get(question_type, ""))
    
    if not prompt:
        return None
    
    try:
        # RAG 시스템으로 질문 생성
        from utils.model_loader import generate_response
        generated_question = generate_response(model_interface, prompt, max_tokens=100)
        
        # 생성된 질문 정제
        if generated_question and len(generated_question.strip()) > 10:
            # 불필요한 부분 제거
            cleaned_question = generated_question.strip()
            if cleaned_question.startswith("Question:"):
                cleaned_question = cleaned_question[9:].strip()
            elif cleaned_question.startswith("Situation:"):
                cleaned_question = cleaned_question[10:].strip()
            
            return cleaned_question
            
    except Exception as e:
        st.error(f"RAG 질문 생성 오류: {e}")
        
    return None

def _generate_simple_feedback(answer):
    """답변에 대한 간단한 피드백 생성 (선택적)"""
    if len(answer.strip()) < 20:
        return "💡 Try to provide more detailed answers to showcase your English skills better!"
    elif len(answer.strip()) > 200:
        return "👍 Great detailed response! Well done!"
    else:
        return "👍 Good answer!"

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
