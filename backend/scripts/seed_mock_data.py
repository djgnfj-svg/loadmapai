"""
Seed mock data for test account
"""
import uuid
from datetime import date, timedelta
from app.db import SessionLocal
from app.models import User, Roadmap, MonthlyGoal, WeeklyTask, DailyTask
from app.models.roadmap import RoadmapMode, RoadmapStatus
from app.models.monthly_goal import TaskStatus


def seed_mock_data():
    db = SessionLocal()

    try:
        # Find test user
        user = db.query(User).filter(User.email == "test@loadmap.ai").first()
        if not user:
            print("Test user not found!")
            return

        print(f"Found test user: {user.email} (ID: {user.id})")

        # Check if user already has roadmaps
        existing = db.query(Roadmap).filter(Roadmap.user_id == user.id).count()
        if existing > 0:
            print(f"User already has {existing} roadmaps. Skipping seed.")
            return

        # === Roadmap 1: Planning Mode - React 프로젝트 ===
        roadmap1 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="React 포트폴리오 프로젝트",
            description="React와 TypeScript를 활용한 포트폴리오 웹사이트 제작 프로젝트입니다.",
            topic="React 포트폴리오 개발",
            duration_months=2,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() + timedelta(days=46),
            mode=RoadmapMode.PLANNING,
            status=RoadmapStatus.ACTIVE,
            progress=35,
        )
        db.add(roadmap1)
        db.flush()

        # Month 1 goals
        month1_r1 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap1.id,
            month_number=1,
            title="프로젝트 기획 및 기본 구조 설계",
            description="프로젝트 요구사항 분석, 와이어프레임 작성, 기본 컴포넌트 구조 설계",
            status=TaskStatus.IN_PROGRESS,
            progress=70,
        )
        db.add(month1_r1)
        db.flush()

        # Week 1
        week1_m1_r1 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month1_r1.id,
            week_number=1,
            title="프로젝트 셋업 및 기획",
            description="Vite + React + TypeScript 프로젝트 생성, 요구사항 정리",
            status=TaskStatus.COMPLETED,
            progress=100,
        )
        db.add(week1_m1_r1)
        db.flush()

        daily_tasks_w1 = [
            ("프로젝트 생성 및 개발환경 설정", "Vite로 React+TS 프로젝트 생성, ESLint/Prettier 설정", True),
            ("디자인 레퍼런스 수집", "Dribbble, Behance에서 포트폴리오 레퍼런스 수집", True),
            ("와이어프레임 작성", "Figma로 메인 페이지 와이어프레임 작성", True),
            ("컴포넌트 구조 설계", "폴더 구조 및 컴포넌트 계층 설계", True),
            ("라우팅 설정", "React Router 설치 및 기본 라우팅 구성", True),
            ("스타일링 도구 설정", "Tailwind CSS 설치 및 설정", True),
            ("Git 저장소 설정", "GitHub 저장소 생성, 초기 커밋", True),
        ]
        for i, (title, desc, checked) in enumerate(daily_tasks_w1, 1):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week1_m1_r1.id,
                day_number=i,
                title=title,
                description=desc,
                status=TaskStatus.COMPLETED if checked else TaskStatus.PENDING,
                is_checked=checked,
            ))

        # Week 2
        week2_m1_r1 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month1_r1.id,
            week_number=2,
            title="헤더 및 히어로 섹션 구현",
            description="네비게이션 바, 히어로 섹션 컴포넌트 개발",
            status=TaskStatus.IN_PROGRESS,
            progress=60,
        )
        db.add(week2_m1_r1)
        db.flush()

        daily_tasks_w2 = [
            ("헤더 컴포넌트 구현", "반응형 네비게이션 바 컴포넌트 개발", True),
            ("히어로 섹션 레이아웃", "히어로 섹션 기본 구조 및 스타일링", True),
            ("타이핑 애니메이션 추가", "자기소개 텍스트 타이핑 효과 구현", True),
            ("스크롤 애니메이션", "섹션 진입 시 fade-in 애니메이션 추가", True),
            ("다크모드 토글 구현", "다크/라이트 모드 전환 기능 개발", False),
            ("반응형 디자인 적용", "모바일/태블릿 대응 스타일 작성", False),
            ("코드 리팩토링", "컴포넌트 분리 및 코드 정리", False),
        ]
        for i, (title, desc, checked) in enumerate(daily_tasks_w2, 1):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week2_m1_r1.id,
                day_number=i,
                title=title,
                description=desc,
                status=TaskStatus.COMPLETED if checked else TaskStatus.PENDING,
                is_checked=checked,
            ))

        # Week 3 & 4 (not started)
        week3_m1_r1 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month1_r1.id,
            week_number=3,
            title="프로젝트 섹션 구현",
            description="프로젝트 카드 컴포넌트, 필터링 기능 개발",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(week3_m1_r1)
        db.flush()

        daily_tasks_w3 = [
            ("프로젝트 데이터 구조 설계", "프로젝트 정보 JSON 스키마 정의", False),
            ("프로젝트 카드 컴포넌트", "프로젝트 카드 UI 컴포넌트 개발", False),
            ("카드 호버 효과", "마우스 오버 시 상세정보 표시 효과", False),
            ("필터링 기능 구현", "기술 스택별 필터링 기능 추가", False),
            ("프로젝트 상세 모달", "클릭 시 상세 정보 모달 구현", False),
            ("이미지 최적화", "프로젝트 이미지 lazy loading 적용", False),
            ("섹션 통합 테스트", "전체 프로젝트 섹션 동작 확인", False),
        ]
        for i, (title, desc, checked) in enumerate(daily_tasks_w3, 1):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week3_m1_r1.id,
                day_number=i,
                title=title,
                description=desc,
                status=TaskStatus.COMPLETED if checked else TaskStatus.PENDING,
                is_checked=checked,
            ))

        # Month 2
        month2_r1 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap1.id,
            month_number=2,
            title="컨텐츠 완성 및 배포",
            description="나머지 섹션 구현, 컨텐츠 채우기, Vercel 배포",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month2_r1)
        db.flush()

        week1_m2_r1 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month2_r1.id,
            week_number=1,
            title="About 및 Skills 섹션",
            description="자기소개 및 기술 스택 섹션 구현",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(week1_m2_r1)
        db.flush()

        for i in range(1, 8):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week1_m2_r1.id,
                day_number=i,
                title=f"Day {i} 태스크",
                description="",
                status=TaskStatus.PENDING,
                is_checked=False,
            ))

        # === Roadmap 2: Learning Mode - Python 학습 ===
        roadmap2 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Python 데이터 분석 마스터",
            description="Python을 활용한 데이터 분석 기초부터 시각화까지 학습합니다.",
            topic="Python 데이터 분석",
            duration_months=3,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() + timedelta(days=83),
            mode=RoadmapMode.LEARNING,
            status=RoadmapStatus.ACTIVE,
            progress=15,
        )
        db.add(roadmap2)
        db.flush()

        # Month 1
        month1_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=1,
            title="Python 기초 및 NumPy",
            description="Python 문법 복습, NumPy 배열 연산 학습",
            status=TaskStatus.IN_PROGRESS,
            progress=40,
        )
        db.add(month1_r2)
        db.flush()

        week1_m1_r2 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month1_r2.id,
            week_number=1,
            title="Python 기초 복습",
            description="변수, 자료형, 조건문, 반복문, 함수 복습",
            status=TaskStatus.COMPLETED,
            progress=100,
        )
        db.add(week1_m1_r2)
        db.flush()

        learning_tasks_w1 = [
            ("변수와 자료형", "Python의 기본 자료형과 변수 선언 방법 학습", True),
            ("리스트와 튜플", "리스트, 튜플의 생성과 메서드 활용", True),
            ("딕셔너리와 집합", "딕셔너리, 집합 자료구조 학습", True),
            ("조건문과 반복문", "if/elif/else, for, while 문법 복습", True),
            ("함수 정의와 활용", "함수 정의, 매개변수, 반환값 학습", True),
            ("리스트 컴프리헨션", "리스트 컴프리헨션 문법과 활용", True),
            ("1주차 종합 퀴즈", "Python 기초 전체 복습 퀴즈", True),
        ]
        for i, (title, desc, checked) in enumerate(learning_tasks_w1, 1):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week1_m1_r2.id,
                day_number=i,
                title=title,
                description=desc,
                status=TaskStatus.COMPLETED if checked else TaskStatus.PENDING,
                is_checked=checked,
            ))

        week2_m1_r2 = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=month1_r2.id,
            week_number=2,
            title="NumPy 기초",
            description="NumPy 배열 생성, 인덱싱, 연산 학습",
            status=TaskStatus.IN_PROGRESS,
            progress=30,
        )
        db.add(week2_m1_r2)
        db.flush()

        learning_tasks_w2 = [
            ("NumPy 소개와 설치", "NumPy 라이브러리 소개, 설치 및 import", True),
            ("배열 생성하기", "np.array, np.zeros, np.ones, np.arange 학습", True),
            ("배열 인덱싱과 슬라이싱", "다차원 배열 인덱싱, 슬라이싱 기법", False),
            ("배열 연산", "요소별 연산, 브로드캐스팅 개념 학습", False),
            ("통계 함수 활용", "mean, sum, std, min, max 등 통계 함수", False),
            ("배열 변형", "reshape, flatten, transpose 활용", False),
            ("2주차 종합 퀴즈", "NumPy 기초 전체 복습 퀴즈", False),
        ]
        for i, (title, desc, checked) in enumerate(learning_tasks_w2, 1):
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week2_m1_r2.id,
                day_number=i,
                title=title,
                description=desc,
                status=TaskStatus.COMPLETED if checked else TaskStatus.PENDING,
                is_checked=checked,
            ))

        # Month 2 & 3 placeholder
        month2_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=2,
            title="Pandas 데이터 처리",
            description="Pandas DataFrame 활용, 데이터 전처리 기법 학습",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month2_r2)

        month3_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=3,
            title="데이터 시각화",
            description="Matplotlib, Seaborn을 활용한 데이터 시각화",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month3_r2)

        # === Roadmap 3: Completed - 완료된 로드맵 ===
        roadmap3 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Git & GitHub 마스터",
            description="Git 버전 관리와 GitHub 협업 워크플로우를 학습합니다.",
            topic="Git GitHub",
            duration_months=1,
            start_date=date.today() - timedelta(days=45),
            end_date=date.today() - timedelta(days=15),
            mode=RoadmapMode.LEARNING,
            status=RoadmapStatus.COMPLETED,
            progress=100,
        )
        db.add(roadmap3)
        db.flush()

        month1_r3 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap3.id,
            month_number=1,
            title="Git 기초부터 협업까지",
            description="Git 명령어, 브랜치, PR, 협업 워크플로우",
            status=TaskStatus.COMPLETED,
            progress=100,
        )
        db.add(month1_r3)

        db.commit()
        print("Mock data seeded successfully!")
        print(f"Created 3 roadmaps for user {user.email}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_mock_data()
