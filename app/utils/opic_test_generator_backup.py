"""
OPIc 실제 시험 형식 질문 생성 시스템
Survey Value Pool + opic_question.json 기반 RAG 시스템 활용
"""
import random
import json
import os
from typing import List, Dict, Tuple
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
            # 1번: 자기소개 (고정)
            "intro": [
                "Let's start the interview now. Tell me about yourself."
            ],
            
            # 2-4번: Survey 기반 기본 세트
            "survey_basic": {
                "work": [
                    "Tell me about your work experience.",
                    "What do you like most about your job?",
                    "Describe a typical day at your workplace."
                ],
                "education": [
                    "Tell me about your school life.",
                    "What subjects do you enjoy studying?",
                    "How do you prepare for exams?"
                ],
                "living": [
                    "Describe where you live.",
                    "What do you like about your living situation?",
                    "How do you spend time at home?"
                ],
                "leisure": [
                    "What do you do for entertainment?",
                    "Tell me about the last movie you watched.",
                    "Where do you usually go for fun?"
                ],
                "hobbies": [
                    "What are your hobbies?",
                    "How did you get interested in this hobby?",
                    "Do you have any creative activities you enjoy?"
                ],
                "sports": [
                    "What sports do you like?",
                    "How often do you exercise?",
                    "Describe your favorite sport to me."
                ],
                "travel": [
                    "Tell me about a memorable trip you took.",
                    "Where would you like to travel next?",
                    "Do you prefer domestic or international travel?"
                ]
            },
            
            # 5-7번: 돌발 질문 (Survey와 무관한 일반적 주제)
            "unexpected": {
                "level_1": [
                    "What is your favorite food?",
                    "What color do you like?", 
                    "What day is today?"
                ],
                "level_2": [
                    "Tell me about your favorite food.",
                    "What do you usually wear?",
                    "What do you do in the morning?"
                ],
                "level_3": [
                    "Describe your favorite season and why you like it.",
                    "Tell me about a restaurant you like to go to.",
                    "What do you usually do on weekends?"
                ],
                "level_4": [
                    "Describe your ideal weekend and explain what makes it special.",
                    "Tell me about a memorable birthday celebration you had or attended.",
                    "What kind of music do you enjoy and how does it make you feel?"
                ],
                "level_5": [
                    "How do you think weather affects people's mood and daily activities?",
                    "Describe how your taste in music has changed over the years and what influenced these changes.",
                    "Compare the advantages and disadvantages of eating at home versus eating out."
                ],
                "level_6": [
                    "Analyze how seasonal changes impact different industries and people's lifestyle choices.",
                    "Discuss the cultural significance of food in building social relationships and community bonds.",
                    "Evaluate the role of music in modern society and its influence on youth culture."
                ]
            },
            
            # 8-10번: Survey 기반 심화 세트  
            "survey_advanced": {
                "work": [
                    "What challenges do you face at work and how do you overcome them?",
                    "How has your work experience changed you as a person?",
                    "What advice would you give to someone starting in your field?"
                ],
                "education": [
                    "How do you think education has changed over the years?",
                    "What study methods work best for you and why?",
                    "How do you balance your studies with other activities?"
                ],
                "living": [
                    "How has your living situation influenced your daily habits?",
                    "What changes would you make to improve your living environment?",
                    "How do you maintain good relationships with people you live with?"
                ],
                "leisure": [
                    "How have your entertainment preferences changed over time?",
                    "What role does entertainment play in your life?",
                    "How do you choose what movies or shows to watch?"
                ],
                "hobbies": [
                    "How have your hobbies helped you grow as a person?",
                    "What challenges have you faced while pursuing your hobbies?",
                    "How do you find time for your hobbies in your busy schedule?"
                ],
                "sports": [
                    "How do sports or exercise affect your daily life?",
                    "What benefits have you gained from playing sports?",
                    "How do you motivate yourself to stay active?"
                ],
                "travel": [
                    "How do you plan your trips and what do you consider important?",
                    "What have you learned from your travel experiences?",
                    "How do you handle unexpected situations while traveling?"
                ]
            },
            
            # 11-13번: 롤플레잉 상황별 질문
            "roleplay": {
                "level_1": [
                    "You want to buy food. What do you say?",
                    "You want to know the time. Ask someone.",
                    "Say hello to a new person."
                ],
                "level_2": [
                    "You are at a store. Ask about the price of something.",
                    "You want to go to the bathroom. Ask where it is.",
                    "Order your favorite food at a restaurant."
                ],
                "level_3": [
                    "You are at a restaurant and your order is wrong. What do you tell the waiter?",
                    "You want to return something you bought. Talk to the store clerk.",
                    "You are late for meeting a friend. Call them and explain."
                ],
                "level_4": [
                    "You are at a restaurant and there's a problem with your order. Explain the situation and ask for a solution.",
                    "You need to return a defective item to a store. Describe the problem to the store clerk.",
                    "You want to join a gym. Ask about membership options, prices, and facilities."
                ],
                "level_5": [
                    "You are organizing a surprise party for a friend. Call other friends to ask for help and coordinate the plans.",
                    "You need to reschedule an important meeting due to an emergency. Explain the situation professionally to your colleague.",
                    "You want to make a complaint about poor service at a hotel. Explain the problems to the manager and suggest solutions."
                ],
                "level_6": [
                    "You are mediating a conflict between two colleagues at work. Address both parties and help them find a resolution.",
                    "You need to negotiate rental terms for a new apartment. Discuss conditions, price, and make counteroffers with the landlord.",
                    "You are presenting a new business proposal to potential investors. Explain your idea, address their concerns, and persuade them."
                ]
            },
            
            # 14-15번: 사회 이슈 고난도 질문
            "social_issues": {
                "level_1": [
                    "Do you like using phones?",
                    "Is school important?",
                    "Do you like your city?"
                ],
                "level_2": [
                    "What do you think about phones?",
                    "Tell me about school.",
                    "What do you like about your city?"
                ],
                "level_3": [
                    "How do you use your phone every day?",
                    "What do you think about online classes?",
                    "How is your city changing?"
                ],
                "level_4": [
                    "What do you think about the impact of social media on young people?",
                    "How has technology changed the way people work?",
                    "What are your thoughts on environmental protection in your community?"
                ],
                "level_5": [
                    "How do you think social media is changing the way people communicate and maintain relationships?",
                    "What are the advantages and disadvantages of remote work becoming more common?",
                    "How do you think people can balance economic development with environmental protection?"
                ],
                "level_6": [
                    "Analyze the long-term societal implications of artificial intelligence and automation on employment and human relationships.",
                    "Evaluate the role of government versus individual responsibility in addressing climate change and environmental sustainability.",
                    "Discuss how globalization and digital technology are reshaping cultural identity and cross-cultural understanding in the modern world."
                ]
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
        
        # 15문항 생성
        self._generate_all_questions()
    
    def _categorize_survey_pool(self) -> Dict[str, List[str]]:
        """Survey Value Pool을 카테고리별로 분류"""
        categories = {
            "work": [],
            "education": [], 
            "living": [],
            "leisure": [],
            "hobbies": [],
            "sports": [],
            "travel": []
        }
        
        # 카테고리별 키워드 매핑
        keyword_mapping = {
            "work": ["work", "experience", "job", "searching", "business"],
            "education": ["student", "school", "university", "education", "study"],
            "living": ["living", "house", "apartment", "dormitory", "family", "friends"],
            "leisure": ["movies", "club", "performance", "concert", "museum", "park", "cafe", "bar"],
            "hobbies": ["music", "reading", "cooking", "pets", "drawing", "writing", "investing", "newspaper", "photos"],
            "sports": ["basketball", "volleyball", "tennis", "swimming", "taekwondo", "jogging", "yoga", "health", "exercise"],
            "travel": ["travel", "trip", "business trip", "staycation", "domestic", "international"]
        }
        
        for item in self.survey_value_pool:
            if item.startswith("level_"):
                continue
                
            item_lower = item.lower()
            for category, keywords in keyword_mapping.items():
                if any(keyword in item_lower for keyword in keywords):
                    categories[category].append(item)
                    break
        
        return categories
    
    def _generate_all_questions(self) -> None:
        """15문항 모두 생성"""
        categories = self._categorize_survey_pool()
        
        # 가장 많은 항목을 가진 카테고리들 찾기
        main_categories = sorted(categories.keys(), 
                               key=lambda x: len(categories[x]), 
                               reverse=True)[:3]  # 상위 3개 카테고리
        
        # 1번: 자기소개 (고정)
        self.questions.append({
            "number": 1,
            "type": "intro",
            "question": self.question_sets["intro"][0]
        })
        
        # 2-4번: Survey 기반 기본 세트
        self._add_survey_questions(2, 4, main_categories, "survey_basic")
        
        # 5-7번: 돌발 질문
        self._add_unexpected_questions(5, 7)
        
        # 8-10번: Survey 기반 심화 세트
        self._add_survey_questions(8, 10, main_categories, "survey_advanced")
        
        # 11-13번: 롤플레잉
        self._add_roleplay_questions(11, 13)
        
        # 14-15번: 사회 이슈
        self._add_social_issues_questions(14, 15)
    
    def _add_survey_questions(self, start: int, end: int, categories: List[str], question_type: str) -> None:
        """Survey 기반 질문 추가"""
        questions_to_add = end - start + 1
        available_questions = []
        
        # 주요 카테고리에서 질문 수집
        for category in categories:
            if category in self.question_sets[question_type]:
                available_questions.extend([
                    (category, q) for q in self.question_sets[question_type][category]
                ])
        
        # 질문이 부족하면 모든 카테고리에서 추가
        if len(available_questions) < questions_to_add:
            for category in self.question_sets[question_type]:
                if category not in categories:
                    available_questions.extend([
                        (category, q) for q in self.question_sets[question_type][category]
                    ])
        
        # 무작위로 선택
        selected = random.sample(available_questions, min(questions_to_add, len(available_questions)))
        
        for i, (category, question) in enumerate(selected):
            self.questions.append({
                "number": start + i,
                "type": f"{question_type}_{category}",
                "question": question
            })
    
    def _add_unexpected_questions(self, start: int, end: int) -> None:
        """돌발 질문 추가 - 난이도별"""
        questions_to_add = end - start + 1
        level_questions = self.question_sets["unexpected"].get(self.user_level, 
                                                             self.question_sets["unexpected"]["level_3"])
        
        # 필요한 수만큼 질문 선택 (중복 허용)
        selected = []
        available_questions = level_questions.copy()
        
        for _ in range(questions_to_add):
            if not available_questions:
                available_questions = level_questions.copy()  # 재사용
            question = random.choice(available_questions)
            selected.append(question)
            available_questions.remove(question)
        
        for i, question in enumerate(selected):
            self.questions.append({
                "number": start + i,
                "type": "unexpected",
                "question": question
            })
    
    def _add_roleplay_questions(self, start: int, end: int) -> None:
        """롤플레잉 질문 추가"""
        questions_to_add = end - start + 1
        selected = random.sample(self.question_sets["roleplay"], questions_to_add)
        
        for i, question in enumerate(selected):
            self.questions.append({
                "number": start + i,
                "type": "roleplay",
                "question": question
            })
    
    def _add_social_issues_questions(self, start: int, end: int) -> None:
        """사회 이슈 질문 추가"""
        questions_to_add = end - start + 1
        selected = random.sample(self.question_sets["social_issues"], questions_to_add)
        
        for i, question in enumerate(selected):
            self.questions.append({
                "number": start + i,
                "type": "social_issues", 
                "question": question
            })
    
    def get_current_question(self) -> Dict:
        """현재 질문 가져오기"""
        if self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None
    
    def get_next_question(self) -> Dict:
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
        base_type = question_type.split('_')[0] + '_' + question_type.split('_')[1] if '_' in question_type else question_type
        return descriptions.get(base_type, descriptions.get(question_type, "❓ 질문"))
