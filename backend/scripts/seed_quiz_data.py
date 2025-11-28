"""
Seed quiz mock data for learning mode tasks
5 questions per quiz: 3 multiple choice + 1 short answer + 1 essay
"""
import uuid
from app.db import SessionLocal
from app.models import User, Roadmap, DailyTask, Quiz, Question
from app.models.quiz import QuizStatus
from app.models.question import QuestionType
from app.models.roadmap import RoadmapMode


def seed_quiz_data():
    db = SessionLocal()

    try:
        # Find test user
        user = db.query(User).filter(User.email == "test@loadmap.ai").first()
        if not user:
            print("Test user not found!")
            return

        print(f"Found test user: {user.email}")

        # Delete existing quizzes for fresh start
        existing_quizzes = db.query(Quiz).filter(Quiz.user_id == user.id).all()
        for q in existing_quizzes:
            db.delete(q)
        db.commit()
        print(f"Deleted {len(existing_quizzes)} existing quizzes")

        # Find learning mode roadmaps
        learning_roadmaps = db.query(Roadmap).filter(
            Roadmap.user_id == user.id,
            Roadmap.mode == RoadmapMode.LEARNING
        ).all()

        print(f"Found {len(learning_roadmaps)} learning roadmaps")

        # Quiz templates for different topics - each with 5 questions
        quiz_templates = {
            "변수와 자료형": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 정수형 변수를 선언하는 올바른 방법은?",
                    "options": ["int x = 5", "x = 5", "var x = 5", "let x = 5"],
                    "answer": "B",
                    "explanation": "Python은 동적 타입 언어로, 변수 선언 시 타입을 명시하지 않습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "다음 중 Python의 기본 자료형이 아닌 것은?",
                    "options": ["int", "str", "array", "bool"],
                    "answer": "C",
                    "explanation": "array는 Python의 기본 자료형이 아니라 별도의 모듈에서 제공합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "type(3.14)의 결과는?",
                    "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'number'>"],
                    "answer": "B",
                    "explanation": "Python에서 소수점이 있는 숫자는 float 타입입니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "문자열을 정수로 변환하는 Python 내장 함수의 이름은?",
                    "answer": "int",
                    "explanation": "int() 함수를 사용하여 문자열을 정수로 변환할 수 있습니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "Python에서 동적 타입 언어의 장단점을 설명하세요.",
                    "answer": "장점: 코드 작성이 간결, 유연성 높음. 단점: 런타임 오류 가능성, 성능 저하",
                    "explanation": "동적 타입 언어는 변수 선언 시 타입을 지정하지 않아 유연하지만, 타입 관련 오류를 실행 시점에 발견하게 됩니다."
                },
            ],
            "리스트와 튜플": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트와 튜플의 가장 큰 차이점은?",
                    "options": ["리스트는 숫자만 저장", "튜플은 수정 불가능", "리스트는 순서 없음", "튜플은 중복 불가"],
                    "answer": "B",
                    "explanation": "튜플(tuple)은 불변(immutable) 자료형으로, 생성 후 수정할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트에 요소를 추가하는 메서드는?",
                    "options": ["add()", "append()", "insert_end()", "push()"],
                    "answer": "B",
                    "explanation": "append() 메서드는 리스트의 끝에 새로운 요소를 추가합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "[1, 2, 3][1]의 결과는?",
                    "options": ["1", "2", "3", "오류 발생"],
                    "answer": "B",
                    "explanation": "Python의 인덱스는 0부터 시작하므로, [1]은 두 번째 요소인 2를 반환합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "리스트 [1, 2, 3]의 길이를 구하는 함수는?",
                    "answer": "len",
                    "explanation": "len() 함수를 사용하여 리스트의 길이를 구할 수 있습니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "리스트 슬라이싱에 대해 예시와 함께 설명하세요.",
                    "answer": "list[start:end:step] 형태로 리스트의 일부를 추출. 예: [1,2,3,4,5][1:4]는 [2,3,4]",
                    "explanation": "슬라이싱은 시작 인덱스부터 끝 인덱스 전까지의 요소를 추출합니다."
                },
            ],
            "딕셔너리와 집합": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "딕셔너리에서 키(key)로 사용할 수 없는 타입은?",
                    "options": ["문자열", "정수", "리스트", "튜플"],
                    "answer": "C",
                    "explanation": "딕셔너리의 키는 해시 가능해야 하므로, 변경 가능한 리스트는 키로 사용할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "집합(set)의 특징이 아닌 것은?",
                    "options": ["중복 불허", "순서 없음", "인덱싱 가능", "변경 가능"],
                    "answer": "C",
                    "explanation": "집합은 순서가 없기 때문에 인덱스로 요소에 접근할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "딕셔너리 {'a': 1, 'b': 2}에서 키 'a'의 값을 가져오는 방법은?",
                    "options": ["dict.a", "dict['a']", "dict.get['a']", "dict(a)"],
                    "answer": "B",
                    "explanation": "딕셔너리는 대괄호와 키를 사용하여 값에 접근합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "두 집합의 합집합을 구하는 메서드 이름은?",
                    "answer": "union",
                    "explanation": "union() 메서드 또는 | 연산자로 합집합을 구할 수 있습니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "딕셔너리의 주요 활용 사례를 2가지 이상 설명하세요.",
                    "answer": "1) 데이터 저장 (JSON 형태), 2) 빈도수 계산, 3) 캐싱, 4) 설정값 관리 등",
                    "explanation": "딕셔너리는 키-값 쌍으로 데이터를 효율적으로 관리할 수 있는 자료구조입니다."
                },
            ],
            "NumPy 소개와 설치": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy를 import하는 가장 일반적인 방법은?",
                    "options": ["import numpy", "import numpy as np", "from numpy import *", "import np"],
                    "answer": "B",
                    "explanation": "관례적으로 NumPy는 'np'라는 별칭으로 import합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy의 주요 장점이 아닌 것은?",
                    "options": ["빠른 배열 연산", "메모리 효율성", "웹 개발 지원", "수학 함수 제공"],
                    "answer": "C",
                    "explanation": "NumPy는 수치 계산에 특화된 라이브러리입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy 배열과 Python 리스트의 차이점은?",
                    "options": ["리스트가 더 빠름", "NumPy는 동일 타입만 저장", "리스트는 수정 불가", "차이 없음"],
                    "answer": "B",
                    "explanation": "NumPy 배열은 동일한 데이터 타입의 요소만 저장하여 메모리 효율적입니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "NumPy를 설치하는 pip 명령어는? (pip install ___)",
                    "answer": "numpy",
                    "explanation": "pip install numpy 명령어로 NumPy를 설치할 수 있습니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "NumPy가 데이터 분석에서 중요한 이유를 설명하세요.",
                    "answer": "빠른 수치 연산, 벡터화 연산 지원, 다른 라이브러리(Pandas, Scikit-learn)의 기반",
                    "explanation": "NumPy는 Python 데이터 과학 생태계의 핵심 라이브러리입니다."
                },
            ],
            "배열 생성하기": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "모든 요소가 0인 3x3 배열을 만드는 함수는?",
                    "options": ["np.zeros((3,3))", "np.empty((3,3))", "np.null((3,3))", "np.zero(3,3)"],
                    "answer": "A",
                    "explanation": "np.zeros((3,3))는 3x3 크기의 0으로 채워진 배열을 생성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "np.arange(5)의 결과는?",
                    "options": ["[0,1,2,3,4,5]", "[1,2,3,4,5]", "[0,1,2,3,4]", "[5]"],
                    "answer": "C",
                    "explanation": "np.arange(5)는 0부터 4까지의 배열을 생성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "np.ones((2,3))의 shape은?",
                    "options": ["(3,2)", "(2,3)", "(6,)", "(2,3,1)"],
                    "answer": "B",
                    "explanation": "np.ones((2,3))는 2행 3열의 배열을 생성합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "0부터 10까지 2 간격으로 배열을 만드는 함수는? np.___(0, 11, 2)",
                    "answer": "arange",
                    "explanation": "np.arange(0, 11, 2)는 [0, 2, 4, 6, 8, 10]을 생성합니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "np.zeros, np.ones, np.empty의 차이점을 설명하세요.",
                    "answer": "zeros: 0으로 초기화, ones: 1로 초기화, empty: 초기화 없이 메모리 할당만 (임의값)",
                    "explanation": "각 함수는 다른 초기값으로 배열을 생성합니다."
                },
            ],
            "default": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "이 학습 내용에 대한 이해도를 확인하는 문제입니다.",
                    "options": ["매우 이해함", "이해함", "보통", "이해 못함"],
                    "answer": "A",
                    "explanation": "학습 내용을 잘 이해했는지 확인하세요."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "학습한 내용 중 가장 중요한 개념은?",
                    "options": ["기본 문법", "응용 방법", "실제 활용", "모두 중요"],
                    "answer": "D",
                    "explanation": "모든 개념이 서로 연결되어 중요합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "추가 학습이 필요한 부분은?",
                    "options": ["없음", "일부 개념", "대부분", "전체"],
                    "answer": "B",
                    "explanation": "지속적인 복습과 실습이 중요합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "오늘 학습한 핵심 키워드를 하나 작성하세요.",
                    "answer": "학습",
                    "explanation": "핵심 개념을 정리하는 것이 중요합니다."
                },
                {
                    "type": QuestionType.ESSAY,
                    "text": "오늘 학습한 내용을 간단히 요약해 보세요.",
                    "answer": "학습 내용 요약",
                    "explanation": "자신만의 언어로 정리하면 이해도가 높아집니다."
                },
            ],
        }

        quiz_count = 0

        for roadmap in learning_roadmaps:
            for goal in roadmap.monthly_goals:
                for week in goal.weekly_tasks:
                    for task in week.daily_tasks:
                        # Find matching template or use default
                        template_key = None
                        for key in quiz_templates.keys():
                            if key != "default" and key in task.title:
                                template_key = key
                                break

                        if not template_key:
                            template_key = "default"

                        questions_data = quiz_templates[template_key]

                        # Create quiz
                        quiz = Quiz(
                            id=uuid.uuid4(),
                            daily_task_id=task.id,
                            user_id=user.id,
                            status=QuizStatus.PENDING,
                            total_questions=len(questions_data),
                            score=None,
                            correct_count=None,
                            feedback_summary=None,
                        )
                        db.add(quiz)
                        db.flush()

                        # Create questions (5 per quiz)
                        for i, q_data in enumerate(questions_data, 1):
                            question = Question(
                                id=uuid.uuid4(),
                                quiz_id=quiz.id,
                                question_number=i,
                                question_type=q_data["type"],
                                question_text=q_data["text"],
                                options=q_data.get("options"),
                                correct_answer=q_data["answer"],
                                explanation=q_data["explanation"],
                                points=20 if q_data["type"] == QuestionType.ESSAY else
                                       15 if q_data["type"] == QuestionType.SHORT_ANSWER else 10,
                            )
                            db.add(question)

                        quiz_count += 1
                        print(f"  Created quiz for: {task.title} ({len(questions_data)} questions)")

        db.commit()
        print(f"\nTotal quizzes created: {quiz_count}")
        print("Each quiz has 5 questions: 3 multiple choice + 1 short answer + 1 essay")

    except Exception as e:
        db.rollback()
        print(f"Error seeding quiz data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_quiz_data()
