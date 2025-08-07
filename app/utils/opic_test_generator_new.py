"""
OPIc 실제 시험 형식 질문 생성 시스템
Survey Value Pool + opic_question.json 기반 RAG 시스템 활용
"""
import random
import json
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class OPIcTestGenerator:
    """OPIc 실제 시험 형식으로 15문항을 생성하는 클래스"""
    
    def __init__(self):
        self.current_question = 0
        self.total_questions = 15
        self.survey_value_pool = []
        self.questions = []
        self.user_level = "level_3"  # 기본값
        
        # opic_question.json 데이터 로드
        self.opic_questions = self._load_opic_questions()
        
    def _load_opic_questions(self) -> Dict:
        """opic_question.json 파일에서 질문 데이터를 로드합니다."""
        try:
            # 프로젝트 루트에서 data/opic_question.json 찾기
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            json_path = project_root / "data" / "opic_question.json"
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"❌ OPIc 질문 파일을 찾을 수 없습니다: {json_path}")
                return self._get_fallback_questions()
        except Exception as e:
            print(f"❌ OPIc 질문 파일 로딩 오류: {e}")
            return self._get_fallback_questions()
    
    def _get_fallback_questions(self) -> Dict:
        """JSON 파일을 로드할 수 없을 때 사용할 기본 질문들"""
        return {
            "survey": {
                "movies": ["What kind of movies do you enjoy watching?"],
                "music": ["What type of music do you listen to?"],
                "sports": ["What sports do you like to play or watch?"]
            },
            "role_play": {
                "general": ["I'd like to give you a situation to act out..."]
            }
        }
    
    def initialize_test(self, survey_value_pool: List[str]) -> None:
        """시험 초기화 및 15문항 생성"""
        self.survey_value_pool = survey_value_pool
        self.current_question = 0
        self.questions = []
        
        # Self Assessment 레벨 추출
        for item in survey_value_pool:
            if item.startswith("level_"):
                self.user_level = item
                break
        
        print(f"🎯 OPIc 시험 초기화: {len(survey_value_pool)}개 항목, {self.user_level}")
        
        # 15문항 생성
        self._generate_all_questions()
    
    def _generate_all_questions(self) -> None:
        """실제 OPIc JSON 데이터를 활용하여 15문항 생성"""
        # 1번: 자기소개 (고정)
        self.questions.append({
            "number": 1,
            "type": "intro",
            "question": "Let's start the interview now. Tell me about yourself."
        })
        
        # Survey Value Pool에서 실제 키워드 추출
        survey_keywords = [item for item in self.survey_value_pool if not item.startswith("level_")]
        
        # 2-4번: Survey 기반 기본 세트
        self._add_survey_questions_from_json(2, 4, survey_keywords, "basic")
        
        # 5-7번: 돌발 질문 (일반 주제)
        self._add_unexpected_questions(5, 7)
        
        # 8-10번: Survey 기반 심화 세트
        self._add_survey_questions_from_json(8, 10, survey_keywords, "advanced")
        
        # 11-13번: 롤플레잉
        self._add_roleplay_questions(11, 13)
        
        # 14-15번: 사회 이슈 (고난도)
        self._add_social_issues_questions(14, 15)
    
    def _add_survey_questions_from_json(self, start: int, end: int, keywords: List[str], level: str) -> None:
        """JSON 데이터에서 Survey Value Pool 기반 질문 추가"""
        questions_to_add = end - start + 1
        selected_questions = []
        
        # Survey Value Pool의 키워드와 JSON의 키 매칭
        for keyword in keywords:
            if keyword in self.opic_questions.get("survey", {}):
                # 해당 키워드의 질문들 가져오기
                available_questions = self.opic_questions["survey"][keyword]
                if available_questions:
                    # 레벨에 따라 질문 선택
                    question = self._select_question_by_level(available_questions, level)
                    selected_questions.append({
                        "keyword": keyword,
                        "question": question
                    })
        
        # 필요한 개수만큼 질문 선택
        if selected_questions:
            # 충분한 질문이 있으면 무작위 선택, 없으면 재사용
            final_questions = []
            for i in range(questions_to_add):
                if i < len(selected_questions):
                    final_questions.append(selected_questions[i])
                else:
                    # 재사용
                    final_questions.append(selected_questions[i % len(selected_questions)])
            
            # 질문 추가
            for i, q_data in enumerate(final_questions):
                self.questions.append({
                    "number": start + i,
                    "type": f"survey_{level}_{q_data['keyword']}",
                    "question": q_data["question"]
                })
        else:
            # 매칭되는 질문이 없으면 일반 질문 사용
            self._add_general_survey_questions(start, end, level)
    
    def _select_question_by_level(self, questions: List[str], level: str) -> str:
        """사용자 레벨에 따라 적절한 난이도의 질문 선택"""
        if not questions:
            return "Tell me about this topic."
        
        # 레벨별 질문 선택 전략
        if level == "basic":
            # 기본 세트: 첫 번째 질문 (보통 가장 기본적)
            return questions[0]
        elif level == "advanced":
            # 심화 세트: 두 번째 이후 질문 (더 복잡한 질문)
            if len(questions) > 1:
                return questions[random.randint(1, len(questions)-1)]
            else:
                return questions[0]
        else:
            # 무작위 선택
            return random.choice(questions)
    
    def _add_general_survey_questions(self, start: int, end: int, level: str) -> None:
        """매칭되는 키워드가 없을 때 사용할 일반 질문"""
        questions_to_add = end - start + 1
        general_questions = [
            "Tell me about your daily routine.",
            "What do you like to do in your free time?",
            "Describe your hobbies and interests.",
            "Tell me about your work or studies.",
            "What are your future plans?"
        ]
        
        for i in range(questions_to_add):
            question = general_questions[i % len(general_questions)]
            self.questions.append({
                "number": start + i,
                "type": f"survey_{level}_general",
                "question": question
            })
    
    def _add_unexpected_questions(self, start: int, end: int) -> None:
        """돌발 질문 추가 - 난이도별"""
        questions_to_add = end - start + 1
        
        # 사용자 레벨에 따른 돌발 질문
        level_questions = {
            "level_1": [
                "What is your favorite color?",
                "What day is today?",
                "What is the weather like?"
            ],
            "level_2": [
                "Describe your favorite food.",
                "Tell me about your family.",
                "What do you do on weekends?"
            ],
            "level_3": [
                "Describe your favorite season and explain why you like it.",
                "Tell me about a memorable birthday celebration you had.",
                "What kind of music do you enjoy and why?"
            ],
            "level_4": [
                "Tell me about a restaurant you recently visited.",
                "Describe your ideal weekend.",
                "What do you usually do when you feel stressed?"
            ],
            "level_5": [
                "How do you maintain work-life balance?",
                "What changes would you like to see in your community?",
                "How do you handle unexpected problems in daily life?"
            ],
            "level_6": [
                "What's your opinion on the impact of technology on society?",
                "How do you think education should adapt to modern times?",
                "What are the benefits and drawbacks of social media?"
            ]
        }
        
        user_questions = level_questions.get(self.user_level, level_questions["level_3"])
        
        for i in range(questions_to_add):
            question = user_questions[i % len(user_questions)]
            self.questions.append({
                "number": start + i,
                "type": "unexpected",
                "question": question
            })
    
    def _add_roleplay_questions(self, start: int, end: int) -> None:
        """롤플레잉 질문 추가"""
        questions_to_add = end - start + 1
        
        # JSON에서 롤플레잉 질문 가져오기
        roleplay_questions = []
        if "role_play" in self.opic_questions:
            for category, questions in self.opic_questions["role_play"].items():
                roleplay_questions.extend(questions)
        
        # 기본 롤플레잉 질문 (JSON이 없을 때)
        if not roleplay_questions:
            roleplay_questions = [
                "You are at a restaurant and there's a problem with your order. What would you do and say?",
                "You need to return a defective item to a store. Explain the situation to the store clerk.",
                "You want to join a gym. Ask about membership options and prices."
            ]
        
        for i in range(questions_to_add):
            question = roleplay_questions[i % len(roleplay_questions)]
            self.questions.append({
                "number": start + i,
                "type": "roleplay",
                "question": question
            })
    
    def _add_social_issues_questions(self, start: int, end: int) -> None:
        """사회 이슈 질문 추가"""
        questions_to_add = end - start + 1
        
        # 레벨별 사회 이슈 질문
        social_questions = {
            "level_1": [
                "Do you think technology is good or bad?",
                "What do you think about family?"
            ],
            "level_2": [
                "How do you think people use technology?",
                "What is important in education?"
            ],
            "level_3": [
                "What do you think about social media?",
                "How has technology changed our lives?"
            ],
            "level_4": [
                "What are the pros and cons of remote work?",
                "How do you think education should change?"
            ],
            "level_5": [
                "What do you think about work-life balance in modern society?",
                "How do you think artificial intelligence will affect our daily lives?"
            ],
            "level_6": [
                "What do you think about the impact of social media on modern society?",
                "How do you think technology is changing the way people work?",
                "What are your thoughts on environmental protection and climate change?"
            ]
        }
        
        user_questions = social_questions.get(self.user_level, social_questions["level_3"])
        
        for i in range(questions_to_add):
            question = user_questions[i % len(user_questions)]
            self.questions.append({
                "number": start + i,
                "type": "social_issues",
                "question": question
            })
    
    def get_current_question(self) -> Optional[Dict]:
        """현재 질문 가져오기"""
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None
    
    def get_next_question(self) -> Optional[Dict]:
        """다음 질문으로 이동"""
        self.current_question += 1
        return self.get_current_question()
    
    def get_progress(self) -> Tuple[int, int]:
        """진행상황 반환 (현재 문항, 전체 문항)"""
        return (self.current_question + 1, self.total_questions)
    
    def is_test_complete(self) -> bool:
        """시험 완료 여부"""
        return self.current_question >= len(self.questions)
    
    def get_question_type_description(self, question_type: str) -> str:
        """질문 타입별 설명"""
        descriptions = {
            "intro": "🎯 자기소개",
            "survey_basic": "📋 기본 세트 (설문 기반)",
            "unexpected": "⚡ 돌발 세트",
            "survey_advanced": "📈 심화 세트 (설문 기반)",
            "roleplay": "🎭 롤플레잉 세트",
            "social_issues": "🌍 사회 이슈 세트"
        }
        
        # 타입에서 기본 카테고리 추출
        for key, desc in descriptions.items():
            if question_type.startswith(key):
                return desc
        
        return "❓ 질문"
