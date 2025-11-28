"""
Seed quiz mock data for learning mode tasks
5 questions per quiz: 4 multiple choice + 1 short answer
(서술형은 beta - 추후 추가 예정)
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

        # Quiz templates - 4 multiple choice + 1 short answer per topic
        # 정답이 명확한 문제들로 구성
        quiz_templates = {
            "변수와 자료형": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 변수 x에 정수 5를 할당하는 올바른 방법은?",
                    "options": ["int x = 5", "x = 5", "var x = 5", "let x = 5"],
                    "answer": "B",
                    "explanation": "Python은 동적 타입 언어로 타입 선언 없이 x = 5로 할당합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "다음 중 Python의 기본 자료형이 아닌 것은?",
                    "options": ["int", "str", "array", "float"],
                    "answer": "C",
                    "explanation": "array는 기본 자료형이 아니라 별도 모듈(array, numpy)에서 제공합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "type(3.14)의 결과는?",
                    "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'decimal'>"],
                    "answer": "B",
                    "explanation": "Python에서 소수점이 있는 숫자는 float 타입입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "type(True)의 결과는?",
                    "options": ["<class 'int'>", "<class 'str'>", "<class 'bool'>", "<class 'boolean'>"],
                    "answer": "C",
                    "explanation": "True와 False는 bool 타입입니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "문자열 '42'를 정수로 변환하는 함수 이름은? (소문자로 입력)",
                    "answer": "int",
                    "explanation": "int('42')는 정수 42를 반환합니다."
                },
            ],
            "리스트와 튜플": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트와 튜플의 가장 큰 차이점은?",
                    "options": ["리스트는 숫자만 저장 가능", "튜플은 수정 불가능(immutable)", "리스트는 순서가 없음", "튜플은 중복 불가"],
                    "answer": "B",
                    "explanation": "튜플은 생성 후 요소를 변경할 수 없는 불변(immutable) 자료형입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트 끝에 요소를 추가하는 메서드는?",
                    "options": ["add()", "append()", "push()", "insert()"],
                    "answer": "B",
                    "explanation": "append()는 리스트 끝에 요소를 추가합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "[10, 20, 30][1]의 결과는?",
                    "options": ["10", "20", "30", "오류 발생"],
                    "answer": "B",
                    "explanation": "인덱스는 0부터 시작하므로 [1]은 두 번째 요소인 20입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "튜플을 생성하는 올바른 방법은?",
                    "options": ["[1, 2, 3]", "(1, 2, 3)", "{1, 2, 3}", "<1, 2, 3>"],
                    "answer": "B",
                    "explanation": "튜플은 소괄호 ()를 사용하여 생성합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "리스트 [1, 2, 3, 4, 5]의 길이를 구하는 함수 이름은? (소문자로 입력)",
                    "answer": "len",
                    "explanation": "len([1, 2, 3, 4, 5])는 5를 반환합니다."
                },
            ],
            "딕셔너리와 집합": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "딕셔너리에서 키(key)로 사용할 수 없는 타입은?",
                    "options": ["문자열(str)", "정수(int)", "리스트(list)", "튜플(tuple)"],
                    "answer": "C",
                    "explanation": "리스트는 변경 가능(mutable)하여 해시할 수 없으므로 키로 사용 불가합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "집합(set)의 특징이 아닌 것은?",
                    "options": ["중복 불허", "순서 없음", "인덱싱 가능", "변경 가능"],
                    "answer": "C",
                    "explanation": "집합은 순서가 없어서 인덱스로 접근할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "d = {'a': 1, 'b': 2}에서 키 'a'의 값을 가져오는 방법은?",
                    "options": ["d.a", "d['a']", "d.get['a']", "d(a)"],
                    "answer": "B",
                    "explanation": "딕셔너리는 대괄호와 키를 사용하여 d['a']로 값에 접근합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "빈 딕셔너리를 생성하는 방법은?",
                    "options": ["[]", "()", "{}", "set()"],
                    "answer": "C",
                    "explanation": "빈 중괄호 {}는 빈 딕셔너리를 생성합니다. 빈 집합은 set()으로 생성합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "딕셔너리의 모든 키를 반환하는 메서드 이름은? (소문자로 입력)",
                    "answer": "keys",
                    "explanation": "d.keys()는 딕셔너리의 모든 키를 반환합니다."
                },
            ],
            "조건문과 반복문": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 조건문의 올바른 문법은?",
                    "options": ["if (x > 5) {}", "if x > 5:", "if x > 5 then", "if (x > 5):"],
                    "answer": "B",
                    "explanation": "Python 조건문은 if 조건: 형태로 콜론을 사용합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "for i in range(3): 에서 i가 가지는 값은?",
                    "options": ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "1, 2"],
                    "answer": "B",
                    "explanation": "range(3)은 0, 1, 2를 생성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "반복문을 즉시 종료하는 키워드는?",
                    "options": ["stop", "exit", "break", "end"],
                    "answer": "C",
                    "explanation": "break는 반복문을 즉시 종료합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "다음 반복의 처음으로 건너뛰는 키워드는?",
                    "options": ["skip", "continue", "next", "pass"],
                    "answer": "B",
                    "explanation": "continue는 현재 반복을 건너뛰고 다음 반복으로 진행합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "조건이 거짓일 때 실행되는 키워드는? (소문자로 입력)",
                    "answer": "else",
                    "explanation": "else 블록은 if 조건이 거짓일 때 실행됩니다."
                },
            ],
            "함수 정의와 활용": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 함수를 정의하는 키워드는?",
                    "options": ["function", "func", "def", "define"],
                    "answer": "C",
                    "explanation": "Python은 def 키워드로 함수를 정의합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "함수에서 값을 반환하는 키워드는?",
                    "options": ["give", "return", "output", "send"],
                    "answer": "B",
                    "explanation": "return 키워드로 함수의 결과값을 반환합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "def greet(name='Guest'): 에서 'Guest'는 무엇인가?",
                    "options": ["필수 인자", "기본값(default)", "전역 변수", "상수"],
                    "answer": "B",
                    "explanation": "name='Guest'는 인자가 전달되지 않을 때 사용되는 기본값입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "*args의 역할은?",
                    "options": ["키워드 인자 받기", "가변 위치 인자 받기", "리스트 언패킹", "필수 인자 지정"],
                    "answer": "B",
                    "explanation": "*args는 여러 개의 위치 인자를 튜플로 받습니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "이름 없는 간단한 함수를 만드는 키워드는? (소문자로 입력)",
                    "answer": "lambda",
                    "explanation": "lambda x: x + 1 형태로 익명 함수를 만듭니다."
                },
            ],
            "NumPy 소개와 설치": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy를 import하는 관례적인 방법은?",
                    "options": ["import numpy", "import numpy as np", "from numpy import *", "import np"],
                    "answer": "B",
                    "explanation": "NumPy는 관례적으로 np라는 별칭으로 import합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy의 주요 장점이 아닌 것은?",
                    "options": ["빠른 배열 연산", "메모리 효율성", "웹 서버 구축", "수학 함수 제공"],
                    "answer": "C",
                    "explanation": "NumPy는 수치 계산 라이브러리로, 웹 서버 구축과는 관련이 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy 배열의 특징은?",
                    "options": ["다양한 타입 혼합 가능", "동일한 타입만 저장", "크기 변경 자유로움", "순서 없음"],
                    "answer": "B",
                    "explanation": "NumPy 배열은 동일한 데이터 타입만 저장하여 메모리 효율적입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy를 설치하는 pip 명령어는?",
                    "options": ["pip install np", "pip install numpy", "pip get numpy", "pip add numpy"],
                    "answer": "B",
                    "explanation": "pip install numpy로 NumPy를 설치합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "NumPy 배열의 차원 수를 확인하는 속성 이름은? (소문자로 입력)",
                    "answer": "ndim",
                    "explanation": "arr.ndim은 배열의 차원 수를 반환합니다."
                },
            ],
            "배열 생성하기": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "모든 요소가 0인 3x3 배열을 만드는 함수는?",
                    "options": ["np.zeros((3,3))", "np.empty((3,3))", "np.null((3,3))", "np.zero(3,3)"],
                    "answer": "A",
                    "explanation": "np.zeros((3,3))는 0으로 채워진 3x3 배열을 생성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "np.arange(5)의 결과는?",
                    "options": ["[1,2,3,4,5]", "[0,1,2,3,4,5]", "[0,1,2,3,4]", "[5]"],
                    "answer": "C",
                    "explanation": "np.arange(5)는 0부터 4까지의 배열 [0,1,2,3,4]를 생성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "np.ones((2,3))의 shape은?",
                    "options": ["(3,2)", "(2,3)", "(6,)", "(2,3,1)"],
                    "answer": "B",
                    "explanation": "np.ones((2,3))는 2행 3열의 배열을 생성하므로 shape은 (2,3)입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트 [1,2,3]을 NumPy 배열로 변환하는 함수는?",
                    "options": ["np.list([1,2,3])", "np.array([1,2,3])", "np.convert([1,2,3])", "np.make([1,2,3])"],
                    "answer": "B",
                    "explanation": "np.array()로 리스트를 NumPy 배열로 변환합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "배열의 형태(행, 열)를 확인하는 속성 이름은? (소문자로 입력)",
                    "answer": "shape",
                    "explanation": "arr.shape은 배열의 형태를 튜플로 반환합니다."
                },
            ],
            "배열 인덱싱과 슬라이싱": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "arr = np.array([10,20,30,40])에서 arr[2]의 결과는?",
                    "options": ["10", "20", "30", "40"],
                    "answer": "C",
                    "explanation": "인덱스는 0부터 시작하므로 arr[2]는 세 번째 요소인 30입니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "arr[-1]이 의미하는 것은?",
                    "options": ["첫 번째 요소", "마지막 요소", "오류 발생", "빈 배열"],
                    "answer": "B",
                    "explanation": "음수 인덱스 -1은 배열의 마지막 요소를 가리킵니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "arr[1:4]의 결과에 포함되는 인덱스는?",
                    "options": ["1, 2, 3, 4", "1, 2, 3", "0, 1, 2, 3", "2, 3, 4"],
                    "answer": "B",
                    "explanation": "슬라이싱 [1:4]는 인덱스 1, 2, 3을 포함합니다 (4는 제외)."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "arr[::2]의 의미는?",
                    "options": ["처음 2개 요소", "마지막 2개 요소", "2칸씩 건너뛰며 선택", "2번 인덱스부터"],
                    "answer": "C",
                    "explanation": "[::2]는 처음부터 끝까지 2칸 간격으로 요소를 선택합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "배열을 뒤집는 슬라이싱 표현은? (콜론과 마이너스 사용, 예: [::-1])",
                    "answer": "[::-1]",
                    "explanation": "arr[::-1]은 배열을 역순으로 반환합니다."
                },
            ],
            "default": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 주석을 작성하는 기호는?",
                    "options": ["//", "#", "/*", "--"],
                    "answer": "B",
                    "explanation": "Python은 # 기호로 한 줄 주석을 작성합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "print('Hello')의 출력 결과는?",
                    "options": ["'Hello'", "Hello", "hello", "HELLO"],
                    "answer": "B",
                    "explanation": "print()는 따옴표 없이 문자열 내용을 출력합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python 파일의 확장자는?",
                    "options": [".python", ".py", ".pt", ".pyt"],
                    "answer": "B",
                    "explanation": "Python 파일은 .py 확장자를 사용합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "2 + 3 * 4의 결과는?",
                    "options": ["20", "14", "24", "9"],
                    "answer": "B",
                    "explanation": "곱셈이 덧셈보다 우선하므로 3*4=12, 2+12=14입니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "사용자 입력을 받는 함수 이름은? (소문자로 입력)",
                    "answer": "input",
                    "explanation": "input() 함수로 사용자 입력을 받습니다."
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

                        # Create questions (5 per quiz: 4 MC + 1 SA)
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
                                points=20,  # 각 문제 20점, 총 100점
                            )
                            db.add(question)

                        quiz_count += 1
                        print(f"  Created quiz for: {task.title} ({template_key})")

        db.commit()
        print(f"\nTotal quizzes created: {quiz_count}")
        print("Each quiz: 4 multiple choice + 1 short answer = 5 questions (100점 만점)")

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
