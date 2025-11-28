"""
Seed quiz mock data for learning mode tasks
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

        # Find learning mode roadmaps
        learning_roadmaps = db.query(Roadmap).filter(
            Roadmap.user_id == user.id,
            Roadmap.mode == RoadmapMode.LEARNING
        ).all()

        print(f"Found {len(learning_roadmaps)} learning roadmaps")

        # Quiz templates for different topics
        quiz_templates = {
            "변수와 자료형": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "Python에서 정수형 변수를 선언하는 올바른 방법은?",
                    "options": ["int x = 5", "x = 5", "var x = 5", "let x = 5"],
                    "answer": "B",
                    "explanation": "Python은 동적 타입 언어로, 변수 선언 시 타입을 명시하지 않습니다. x = 5와 같이 직접 값을 할당합니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "다음 중 Python의 기본 자료형이 아닌 것은?",
                    "options": ["int", "str", "array", "bool"],
                    "answer": "C",
                    "explanation": "array는 Python의 기본 자료형이 아니라 별도의 모듈에서 제공하는 자료구조입니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "Python에서 문자열을 정수로 변환하는 내장 함수의 이름은?",
                    "answer": "int",
                    "explanation": "int() 함수를 사용하여 문자열을 정수로 변환할 수 있습니다. 예: int('42') = 42"
                },
            ],
            "리스트와 튜플": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트와 튜플의 가장 큰 차이점은?",
                    "options": ["리스트는 숫자만 저장", "튜플은 수정 불가능", "리스트는 순서 없음", "튜플은 중복 불가"],
                    "answer": "B",
                    "explanation": "튜플(tuple)은 불변(immutable) 자료형으로, 한번 생성되면 수정할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "리스트에 요소를 추가하는 메서드는?",
                    "options": ["add()", "append()", "insert_end()", "push()"],
                    "answer": "B",
                    "explanation": "append() 메서드는 리스트의 끝에 새로운 요소를 추가합니다."
                },
                {
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "리스트 [1, 2, 3]의 길이를 구하는 함수는?",
                    "answer": "len",
                    "explanation": "len() 함수를 사용하여 리스트의 길이를 구할 수 있습니다. len([1, 2, 3]) = 3"
                },
            ],
            "딕셔너리와 집합": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "딕셔너리에서 키(key)로 사용할 수 없는 타입은?",
                    "options": ["문자열", "정수", "리스트", "튜플"],
                    "answer": "C",
                    "explanation": "딕셔너리의 키는 해시 가능해야 하므로, 변경 가능한(mutable) 리스트는 키로 사용할 수 없습니다."
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "집합(set)의 특징이 아닌 것은?",
                    "options": ["중복 불허", "순서 없음", "인덱싱 가능", "변경 가능"],
                    "answer": "C",
                    "explanation": "집합은 순서가 없기 때문에 인덱스로 요소에 접근할 수 없습니다."
                },
            ],
            "NumPy 소개와 설치": [
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy를 import하는 가장 일반적인 방법은?",
                    "options": ["import numpy", "import numpy as np", "from numpy import *", "import np"],
                    "answer": "B",
                    "explanation": "관례적으로 NumPy는 'np'라는 별칭으로 import합니다: import numpy as np"
                },
                {
                    "type": QuestionType.MULTIPLE_CHOICE,
                    "text": "NumPy의 주요 장점이 아닌 것은?",
                    "options": ["빠른 배열 연산", "메모리 효율성", "웹 개발 지원", "수학 함수 제공"],
                    "answer": "C",
                    "explanation": "NumPy는 수치 계산에 특화된 라이브러리로, 웹 개발과는 직접적인 관련이 없습니다."
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
                    "type": QuestionType.SHORT_ANSWER,
                    "text": "0부터 9까지의 정수 배열을 만드는 NumPy 함수는?",
                    "answer": "arange",
                    "explanation": "np.arange(10)은 0부터 9까지의 정수 배열을 생성합니다."
                },
            ],
        }

        quiz_count = 0

        for roadmap in learning_roadmaps:
            # Get all daily tasks for this roadmap
            daily_tasks = db.query(DailyTask).join(
                DailyTask.weekly_task
            ).join(
                DailyTask.weekly_task.property.mapper.class_.monthly_goal
            ).filter(
                DailyTask.weekly_task.property.mapper.class_.monthly_goal.property.mapper.class_.roadmap_id == roadmap.id
            ).all()

            # Simpler query - get daily tasks through relationships
            for goal in roadmap.monthly_goals:
                for week in goal.weekly_tasks:
                    for task in week.daily_tasks:
                        # Check if quiz already exists
                        existing_quiz = db.query(Quiz).filter(
                            Quiz.daily_task_id == task.id,
                            Quiz.user_id == user.id
                        ).first()

                        if existing_quiz:
                            continue

                        # Find matching template or use default
                        template_key = None
                        for key in quiz_templates.keys():
                            if key in task.title:
                                template_key = key
                                break

                        if not template_key:
                            # Create a default quiz for other tasks
                            template_key = list(quiz_templates.keys())[quiz_count % len(quiz_templates)]

                        questions_data = quiz_templates.get(template_key, [])

                        if not questions_data:
                            continue

                        # Create quiz
                        quiz = Quiz(
                            id=uuid.uuid4(),
                            daily_task_id=task.id,
                            user_id=user.id,
                            status=QuizStatus.GRADED if task.is_checked else QuizStatus.PENDING,
                            total_questions=len(questions_data),
                            score=85.0 if task.is_checked else None,
                            correct_count=len(questions_data) - 1 if task.is_checked else None,
                            feedback_summary="잘 하셨습니다! 기본 개념을 잘 이해하고 있습니다." if task.is_checked else None,
                        )
                        db.add(quiz)
                        db.flush()

                        # Create questions
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
                                points=10,
                            )
                            db.add(question)

                        quiz_count += 1
                        print(f"  Created quiz for: {task.title}")

        db.commit()
        print(f"\nTotal quizzes created: {quiz_count}")

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
