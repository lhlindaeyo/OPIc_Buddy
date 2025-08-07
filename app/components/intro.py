"""
인트로 화면 컴포넌트
"""
import streamlit as st
import base64
from pathlib import Path
from utils.styles import apply_intro_styles

def show_intro():
    """인트로 화면을 표시합니다."""
    # 스타일 적용
    apply_intro_styles()

    # 타이틀 + 설명
    st.markdown("""
    <div class="block-welcome" style='text-align: center;'>
        <h2 class="opic-header" style="font-size:2.1rem;">
            🔊 <span style='color:#36f; font-weight:bold;'>Oral Proficiency Interview - computer</span>
            <span style='color: #36f; font-weight:bold;'>(OPIc)</span>
        </h2>
        <p style="font-size:1.25rem; font-weight:bold;">지금부터 <span style='color:#f4621f; font-weight:bold;'>English 말하기 평가</span>를 시작하겠습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # Ava 이미지 + 설명
    _display_ava_image()
    
    # 시작 버튼
    _display_start_button()

def _display_ava_image():
    """Ava 이미지를 표시합니다."""
    ava_path = Path(__file__).parent.parent / "ava.png"
    
    if ava_path.exists():
        with open(ava_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        
        st.markdown(
            f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src="data:image/png;base64,{img_base64}" alt="Ava" style="width: 228px;"/>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style='font-size: 1.35rem; font-weight: 600; color: #222; text-align: center; margin-top: 18px; margin-bottom: 40px;'>
            본 인터뷰 평가의 진행자는 Ava입니다.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Ava 이미지를 찾을 수 없습니다.")

def _display_start_button():
    """시작 버튼을 표시합니다."""
    col1, col2, col3 = st.columns([4, 1.5, 4])
    
    with col2:
        if st.button("next", key="start_button", help="opic 모의고사 시작", use_container_width=True):
            st.session_state.stage = "survey"
            st.rerun()
