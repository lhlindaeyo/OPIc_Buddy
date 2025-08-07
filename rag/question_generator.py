"""
OPIc 질문 생성 전용 RAG 시스템
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain.chains import LLMChain
from retriever import retrieve_top_k
import torch

# 환경 변수에서 설정 읽기
PHI15_MODEL_PATH = os.getenv("PHI15_MODEL_PATH", "microsoft/phi-1_5")

# GPU 사용 가능 여부에 따라 device 설정
device = 0 if torch.cuda.is_available() else -1

# 질문 생성용 LLM 로드
try:
    question_gen_pipe = pipeline(
        "text-generation",
        model=PHI15_MODEL_PATH,
        tokenizer=PHI15_MODEL_PATH,
        device=device,
        temperature=0.3,
        max_new_tokens=100,
        do_sample=True
    )
    question_llm = HuggingFacePipeline(pipeline=question_gen_pipe)
    print(f"✅ 질문 생성 모델 로드 성공 (device: {'GPU' if device == 0 else 'CPU'})")
except Exception as e:
    print(f"❌ 질문 생성 모델 로드 실패: {e}")
    question_llm = None

# 질문 생성용 프롬프트 템플릿 (더 간단한 형식)
question_prompt_template = """Based on: {survey_context}

Generate a natural English interview question about {question_type}.

Example questions:
{context}

New question:"""

question_prompt = PromptTemplate(
    input_variables=["context", "survey_context", "question_type"],
    template=question_prompt_template
)

# Chain 생성
if question_llm is not None:
    try:
        question_chain = LLMChain(llm=question_llm, prompt=question_prompt)
        print("✅ 질문 생성 Chain 생성 성공")
    except Exception as e:
        print(f"❌ 질문 생성 Chain 생성 실패: {e}")
        question_chain = None
else:
    question_chain = None


def generate_opic_question(survey_context: str, question_type: str, question_number: int, k: int = 3) -> str:
    """OPIc 질문을 생성합니다."""
    try:
        if question_llm is None or question_chain is None:
            return None
        
        # 1) 관련 컨텍스트 검색
        search_query = f"OPIc question {question_type} {survey_context}"
        contexts = retrieve_top_k(search_query, k)
        
        if not contexts:
            # 컨텍스트가 없으면 일반적인 질문 생성
            contexts = [f"Generate an OPIc question about {question_type}"]
        
        # 2) 컨텍스트를 하나의 문자열로 결합
        merged_context = "\n".join(contexts)
        
        # 3) 질문 생성
        response = question_chain.run(
            context=merged_context[:200],  # 컨텍스트를 짧게 제한
            survey_context=survey_context,
            question_type=question_type
        )
        
        # 4) 응답 정제
        if response and len(response.strip()) > 10:
            # "Question:" 제거 및 정제
            cleaned_question = response.strip()
            if cleaned_question.startswith("Question:"):
                cleaned_question = cleaned_question[9:].strip()
            
            # 줄바꿈과 불필요한 부분 제거
            cleaned_question = cleaned_question.split('\n')[0].strip()
            
            # 너무 길면 자르기
            if len(cleaned_question) > 200:
                cleaned_question = cleaned_question[:200] + "..."
            
            return cleaned_question
            
    except Exception as e:
        print(f"질문 생성 오류: {e}")
        
    return None


def test_question_generation():
    """질문 생성 테스트"""
    test_cases = [
        {
            "survey_context": "living alone, watching sports, TV",
            "question_type": "survey_basic",
            "question_number": 2
        },
        {
            "survey_context": "movies, music, reading",
            "question_type": "survey_advanced",
            "question_number": 8
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n🧪 테스트 케이스 {i+1}:")
        print(f"Survey: {case['survey_context']}")
        print(f"Type: {case['question_type']}")
        
        question = generate_opic_question(
            case["survey_context"],
            case["question_type"],
            case["question_number"]
        )
        
        print(f"Generated Question: {question}")


if __name__ == "__main__":
    test_question_generation()
