import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain.chains import LLMChain

from generator import Phi15Generator
from retriever import retrieve_top_k

# 환경 변수에서 설정 읽기
E5_MODEL_PATH = os.getenv("E5_MODEL_PATH", "intfloat/e5-base-v2")  # 기본값: HuggingFace Hub
PHI15_MODEL_PATH = os.getenv("PHI15_MODEL_PATH", "microsoft/phi-1_5")  # 기본값: HuggingFace Hub

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://hakliml22:Lifegoeson%211@cluster0.1ryjiuy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "OPIcBuddy")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "embedded_opic_samples")

# Generator - GPU 사용 가능 여부에 따라 device 설정
import torch
device = 0 if torch.cuda.is_available() else -1

try:
    hf_pipe = pipeline(
        "text-generation",
        model=PHI15_MODEL_PATH,
        tokenizer=PHI15_MODEL_PATH,
        device=device,
        temperature=0.2,
        max_new_tokens=150,
        do_sample=True
    )
    llm = HuggingFacePipeline(pipeline=hf_pipe)
    print(f"✅ Phi-1.5 모델 로드 성공 (device: {'GPU' if device == 0 else 'CPU'})")
except Exception as e:
    print(f"❌ Phi-1.5 모델 로드 실패: {e}")
    # Fallback: 더 작은 모델 사용
    try:
        hf_pipe = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-small",
            tokenizer="microsoft/DialoGPT-small",
            device=device,
            temperature=0.2,
            max_new_tokens=150
        )
        llm = HuggingFacePipeline(pipeline=hf_pipe)
        print("✅ Fallback 모델 (DialoGPT-small) 로드 성공")
    except Exception as e2:
        print(f"❌ Fallback 모델도 실패: {e2}")
        llm = None

# Prompt 템플릿 정의
prompt_template = """
### [INST]
Instruction: Answer the question based on your knowledge.
Here is context to help:

{context}

### QUESTION:
{question}

[/INST]
"""
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

# Chain 생성 (llm이 로드되었을 때만)
if llm is not None:
    try:
        chain = LLMChain(llm=llm, prompt=prompt)
        print("✅ RAG Chain 생성 성공")
    except Exception as e:
        print(f"❌ RAG Chain 생성 실패: {e}")
        chain = None
else:
    chain = None


def run_rag(question: str, k: int = 3) -> str:
    """RAG 시스템으로 질문에 답변합니다."""
    try:
        if llm is None:
            return "RAG 시스템을 사용할 수 없습니다. 모델 로딩에 실패했습니다."
        
        # 2-1) retrieve_top_k 으로 가장 유사한 k개 문장 가져오기
        contexts = retrieve_top_k(question, k)
        
        if not contexts:
            return f"죄송합니다. '{question}'에 대한 관련 정보를 찾을 수 없습니다. 다른 질문을 해주세요."

        # 2-2) 리스트를 하나의 문자열로 결합
        merged_context = "\n".join(contexts)

        # 2-3) LLMChain에 넘겨서 답변 생성
        response = chain.run(context=merged_context, question=question)
        
        # 응답 정제
        if not response or len(response.strip()) < 10:
            return f"질문 '{question}'에 대해 적절한 답변을 생성하지 못했습니다. 다른 방식으로 질문해보세요."
            
        return response.strip()
        
    except Exception as e:
        return f"RAG 시스템 오류가 발생했습니다: {str(e)[:100]}... 잠시 후 다시 시도해주세요."