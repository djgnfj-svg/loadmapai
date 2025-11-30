"""
Seed mock data for test account
완전한 로드맵 데이터: 모든 월/주/일 태스크 포함
"""
import uuid
from datetime import date, timedelta
from app.db import SessionLocal
from app.models import User, Roadmap, MonthlyGoal, WeeklyTask, DailyTask
from app.models.roadmap import RoadmapMode, RoadmapStatus
from app.models.monthly_goal import TaskStatus


def create_weekly_tasks(db, monthly_goal_id: uuid.UUID, weeks_data: list):
    """Helper to create weekly tasks with daily tasks"""
    for week_num, week_info in enumerate(weeks_data, 1):
        week = WeeklyTask(
            id=uuid.uuid4(),
            monthly_goal_id=monthly_goal_id,
            week_number=week_num,
            title=week_info["title"],
            description=week_info["description"],
            status=week_info.get("status", TaskStatus.PENDING),
            progress=week_info.get("progress", 0),
        )
        db.add(week)
        db.flush()

        for day_num, day_info in enumerate(week_info["days"], 1):
            is_checked = day_info.get("checked", False)
            db.add(DailyTask(
                id=uuid.uuid4(),
                weekly_task_id=week.id,
                day_number=day_num,
                title=day_info["title"],
                description=day_info["description"],
                status=TaskStatus.COMPLETED if is_checked else TaskStatus.PENDING,
                is_checked=is_checked,
            ))


def seed_mock_data():
    db = SessionLocal()

    try:
        # Find test user
        user = db.query(User).filter(User.email == "test@loadmap.ai").first()
        if not user:
            print("Test user not found!")
            return

        print(f"Found test user: {user.email} (ID: {user.id})")

        # Delete existing data for fresh start
        # Delete roadmaps (cascades to monthly_goals, weekly_tasks, daily_tasks)
        existing = db.query(Roadmap).filter(Roadmap.user_id == user.id).all()
        if existing:
            for r in existing:
                db.delete(r)
            db.commit()
            print(f"Deleted {len(existing)} existing roadmaps")

        # ================================================================
        # ROADMAP 1: Planning Mode - React 포트폴리오 프로젝트 (2개월)
        # ================================================================
        roadmap1 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="React 포트폴리오 프로젝트",
            description="React와 TypeScript를 활용하여 개인 포트폴리오 웹사이트를 제작합니다. 반응형 디자인, 다크모드, 애니메이션을 적용하고 Vercel로 배포합니다.",
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

        # Month 1: 기획 및 기본 구조
        month1_r1 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap1.id,
            month_number=1,
            title="프로젝트 기획 및 메인 섹션 개발",
            description="프로젝트 환경 설정, 디자인 기획, 헤더/히어로/프로젝트 섹션 구현",
            status=TaskStatus.IN_PROGRESS,
            progress=70,
        )
        db.add(month1_r1)
        db.flush()

        month1_r1_weeks = [
            {
                "title": "프로젝트 셋업 및 기획",
                "description": "개발 환경 구성, 디자인 레퍼런스 수집, 와이어프레임 작성",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "프로젝트 생성", "description": "Vite + React + TypeScript 프로젝트 생성, 폴더 구조 설정", "checked": True},
                    {"title": "개발 도구 설정", "description": "ESLint, Prettier, Husky 설정으로 코드 품질 관리 환경 구축", "checked": True},
                    {"title": "디자인 레퍼런스 수집", "description": "Dribbble, Behance에서 포트폴리오 디자인 레퍼런스 20개 수집", "checked": True},
                    {"title": "컬러 팔레트 선정", "description": "브랜드 컬러 선정, 다크/라이트 모드 색상 팔레트 정의", "checked": True},
                    {"title": "와이어프레임 작성", "description": "Figma로 전체 페이지 레이아웃 와이어프레임 작성", "checked": True},
                    {"title": "컴포넌트 설계", "description": "재사용 가능한 컴포넌트 목록 정리 및 Props 인터페이스 설계", "checked": True},
                    {"title": "Git 저장소 설정", "description": "GitHub 저장소 생성, README 작성, 초기 커밋", "checked": True},
                ],
            },
            {
                "title": "헤더 및 히어로 섹션",
                "description": "네비게이션 바와 메인 히어로 섹션 개발",
                "status": TaskStatus.IN_PROGRESS,
                "progress": 60,
                "days": [
                    {"title": "Tailwind CSS 설정", "description": "Tailwind CSS 설치, 커스텀 테마 설정, 기본 스타일 정의", "checked": True},
                    {"title": "헤더 컴포넌트 개발", "description": "로고, 네비게이션 메뉴, 모바일 햄버거 메뉴 구현", "checked": True},
                    {"title": "히어로 섹션 레이아웃", "description": "히어로 섹션 기본 구조 및 그리드 레이아웃 구현", "checked": True},
                    {"title": "타이핑 애니메이션", "description": "자기소개 텍스트에 타이핑 효과 애니메이션 적용", "checked": True},
                    {"title": "다크모드 구현", "description": "Context API로 다크/라이트 모드 전환 기능 개발", "checked": False},
                    {"title": "스크롤 애니메이션", "description": "Intersection Observer로 섹션 진입 시 fade-in 효과 적용", "checked": False},
                    {"title": "반응형 테스트", "description": "모바일, 태블릿, 데스크톱 뷰 테스트 및 수정", "checked": False},
                ],
            },
            {
                "title": "프로젝트 섹션 개발",
                "description": "프로젝트 카드 컴포넌트와 필터링 기능 구현",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "프로젝트 데이터 구조", "description": "프로젝트 정보 TypeScript 인터페이스 및 mock 데이터 작성", "checked": False},
                    {"title": "프로젝트 카드 UI", "description": "프로젝트 썸네일, 제목, 설명, 기술스택 표시 카드 컴포넌트", "checked": False},
                    {"title": "호버 인터랙션", "description": "카드 호버 시 오버레이와 상세보기 버튼 표시 효과", "checked": False},
                    {"title": "기술스택 필터", "description": "React, TypeScript, Node.js 등 기술스택별 필터링 기능", "checked": False},
                    {"title": "상세 모달 구현", "description": "프로젝트 클릭 시 상세 정보 모달 팝업 구현", "checked": False},
                    {"title": "이미지 최적화", "description": "프로젝트 이미지 lazy loading, WebP 변환 적용", "checked": False},
                    {"title": "그리드 레이아웃", "description": "Masonry 스타일 그리드 레이아웃 적용", "checked": False},
                ],
            },
            {
                "title": "About 섹션 개발",
                "description": "자기소개 및 경력/학력 타임라인 구현",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "About 레이아웃", "description": "프로필 이미지와 소개 텍스트 2단 레이아웃 구성", "checked": False},
                    {"title": "프로필 이미지 스타일", "description": "프로필 사진에 그라데이션 보더, 호버 효과 적용", "checked": False},
                    {"title": "자기소개 작성", "description": "개발자로서의 철학, 관심 분야, 목표 등 소개글 작성", "checked": False},
                    {"title": "타임라인 컴포넌트", "description": "경력/학력 표시용 수직 타임라인 컴포넌트 개발", "checked": False},
                    {"title": "경력 데이터 입력", "description": "회사명, 기간, 담당 업무 등 경력 정보 입력", "checked": False},
                    {"title": "애니메이션 적용", "description": "스크롤 시 타임라인 아이템 순차 등장 효과", "checked": False},
                    {"title": "섹션 통합 테스트", "description": "About 섹션 전체 동작 및 반응형 테스트", "checked": False},
                ],
            },
        ]
        create_weekly_tasks(db, month1_r1.id, month1_r1_weeks)

        # Month 2: 컨텐츠 완성 및 배포
        month2_r1 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap1.id,
            month_number=2,
            title="나머지 섹션 완성 및 배포",
            description="Skills, Contact 섹션 개발, SEO 최적화, Vercel 배포",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month2_r1)
        db.flush()

        month2_r1_weeks = [
            {
                "title": "Skills 섹션 개발",
                "description": "기술 스택 시각화 및 숙련도 표시",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "스킬 데이터 구조", "description": "기술 스택 카테고리(Frontend, Backend, Tools)별 데이터 정의", "checked": False},
                    {"title": "스킬 카드 컴포넌트", "description": "기술명, 아이콘, 숙련도 레벨 표시 카드 개발", "checked": False},
                    {"title": "숙련도 프로그레스바", "description": "각 기술별 숙련도를 애니메이션 프로그레스바로 표현", "checked": False},
                    {"title": "카테고리 탭", "description": "Frontend/Backend/Tools 카테고리 탭 전환 기능", "checked": False},
                    {"title": "기술 아이콘 적용", "description": "React Icons 또는 Devicon으로 기술 아이콘 적용", "checked": False},
                    {"title": "호버 상세정보", "description": "기술 카드 호버 시 사용 경험, 프로젝트 수 표시", "checked": False},
                    {"title": "반응형 그리드", "description": "화면 크기별 카드 배치 조정", "checked": False},
                ],
            },
            {
                "title": "Contact 섹션 및 Footer",
                "description": "연락처 폼과 소셜 링크, Footer 구현",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Contact 레이아웃", "description": "연락 정보와 문의 폼 2단 레이아웃 구성", "checked": False},
                    {"title": "문의 폼 구현", "description": "이름, 이메일, 메시지 입력 폼 및 유효성 검사", "checked": False},
                    {"title": "EmailJS 연동", "description": "EmailJS로 폼 제출 시 이메일 발송 기능 구현", "checked": False},
                    {"title": "소셜 링크 버튼", "description": "GitHub, LinkedIn, 이메일 등 소셜 링크 아이콘 버튼", "checked": False},
                    {"title": "Footer 컴포넌트", "description": "저작권 표시, 네비게이션 링크, 맨위로 버튼 구현", "checked": False},
                    {"title": "폼 제출 피드백", "description": "제출 성공/실패 토스트 메시지 표시", "checked": False},
                    {"title": "스팸 방지", "description": "reCAPTCHA 또는 허니팟 필드로 스팸 방지 적용", "checked": False},
                ],
            },
            {
                "title": "SEO 및 성능 최적화",
                "description": "검색 엔진 최적화, 성능 개선, 접근성 향상",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "메타 태그 설정", "description": "title, description, Open Graph, Twitter Card 메타 태그 추가", "checked": False},
                    {"title": "시맨틱 HTML", "description": "header, main, section, article 등 시맨틱 태그로 구조 개선", "checked": False},
                    {"title": "이미지 최적화", "description": "모든 이미지 WebP 변환, srcset 반응형 이미지 적용", "checked": False},
                    {"title": "Lighthouse 분석", "description": "Lighthouse로 성능 측정, 90점 이상 달성 목표", "checked": False},
                    {"title": "코드 스플리팅", "description": "React.lazy로 라우트별 코드 스플리팅 적용", "checked": False},
                    {"title": "접근성 개선", "description": "키보드 네비게이션, ARIA 레이블, 색상 대비 검사", "checked": False},
                    {"title": "sitemap 생성", "description": "sitemap.xml, robots.txt 파일 생성", "checked": False},
                ],
            },
            {
                "title": "배포 및 마무리",
                "description": "Vercel 배포, 도메인 연결, 최종 테스트",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Vercel 프로젝트 생성", "description": "Vercel 계정 연결, GitHub 저장소 import", "checked": False},
                    {"title": "환경 변수 설정", "description": "EmailJS API 키 등 환경 변수 Vercel에 설정", "checked": False},
                    {"title": "커스텀 도메인 연결", "description": "개인 도메인 구매 및 Vercel에 연결", "checked": False},
                    {"title": "SSL 인증서 확인", "description": "HTTPS 적용 확인, 보안 설정 점검", "checked": False},
                    {"title": "크로스 브라우저 테스트", "description": "Chrome, Firefox, Safari, Edge 브라우저 테스트", "checked": False},
                    {"title": "최종 QA", "description": "모든 기능 동작 확인, 버그 수정", "checked": False},
                    {"title": "README 업데이트", "description": "프로젝트 설명, 기술 스택, 배포 링크 등 README 완성", "checked": False},
                ],
            },
        ]
        create_weekly_tasks(db, month2_r1.id, month2_r1_weeks)

        # ================================================================
        # ROADMAP 2: Learning Mode - Python 데이터 분석 (3개월)
        # ================================================================
        roadmap2 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Python 데이터 분석 마스터",
            description="Python을 활용한 데이터 분석의 기초부터 실전까지 학습합니다. NumPy, Pandas로 데이터를 처리하고 Matplotlib, Seaborn으로 시각화하는 방법을 익힙니다.",
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

        # Month 1: Python 기초 및 NumPy
        month1_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=1,
            title="Python 기초 및 NumPy",
            description="Python 문법을 복습하고 NumPy 배열 연산의 기초를 학습합니다.",
            status=TaskStatus.IN_PROGRESS,
            progress=40,
        )
        db.add(month1_r2)
        db.flush()

        month1_r2_weeks = [
            {
                "title": "Python 기초 복습",
                "description": "변수, 자료형, 조건문, 반복문, 함수의 기초 문법 복습",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "변수와 자료형", "description": "int, float, str, bool 자료형과 변수 선언, 형변환 학습", "checked": True},
                    {"title": "리스트와 튜플", "description": "리스트/튜플 생성, 인덱싱, 슬라이싱, 메서드(append, extend, pop) 활용", "checked": True},
                    {"title": "딕셔너리와 집합", "description": "딕셔너리 키-값 쌍, 집합의 합집합/교집합/차집합 연산 학습", "checked": True},
                    {"title": "조건문과 반복문", "description": "if/elif/else 조건문, for/while 반복문, break/continue 활용", "checked": True},
                    {"title": "함수 정의와 활용", "description": "def 함수 정의, 매개변수, 반환값, *args/**kwargs 학습", "checked": True},
                    {"title": "리스트 컴프리헨션", "description": "[표현식 for 변수 in 반복가능객체 if 조건] 문법 익히기", "checked": True},
                    {"title": "1주차 복습 퀴즈", "description": "Python 기초 전체 내용 복습 및 퀴즈 풀이", "checked": True},
                ],
            },
            {
                "title": "NumPy 기초",
                "description": "NumPy 배열 생성, 인덱싱, 기본 연산 학습",
                "status": TaskStatus.IN_PROGRESS,
                "progress": 30,
                "days": [
                    {"title": "NumPy 소개와 설치", "description": "NumPy 라이브러리 특징, pip install numpy, import numpy as np", "checked": True},
                    {"title": "배열 생성하기", "description": "np.array(), np.zeros(), np.ones(), np.arange(), np.linspace() 함수", "checked": True},
                    {"title": "배열 인덱싱과 슬라이싱", "description": "1차원/다차원 배열 인덱싱, 슬라이싱 [start:stop:step] 기법", "checked": False},
                    {"title": "배열 연산", "description": "요소별 사칙연산, 브로드캐스팅 개념, 행렬 곱(np.dot, @)", "checked": False},
                    {"title": "통계 함수 활용", "description": "np.mean(), np.sum(), np.std(), np.min(), np.max(), np.argmax()", "checked": False},
                    {"title": "배열 변형", "description": "reshape(), flatten(), transpose(), concatenate(), split()", "checked": False},
                    {"title": "2주차 복습 퀴즈", "description": "NumPy 기초 전체 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "NumPy 심화",
                "description": "고급 인덱싱, 조건부 연산, 파일 입출력",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "불리언 인덱싱", "description": "조건을 만족하는 요소 선택: arr[arr > 5], np.where()", "checked": False},
                    {"title": "팬시 인덱싱", "description": "인덱스 배열로 여러 요소 선택: arr[[1,3,5]], arr[idx]", "checked": False},
                    {"title": "배열 정렬", "description": "np.sort(), np.argsort(), axis 매개변수 활용", "checked": False},
                    {"title": "고유값과 빈도", "description": "np.unique(), return_counts 옵션으로 빈도 계산", "checked": False},
                    {"title": "난수 생성", "description": "np.random.rand(), randn(), randint(), choice(), seed()", "checked": False},
                    {"title": "파일 입출력", "description": "np.save(), np.load(), np.savetxt(), np.loadtxt()", "checked": False},
                    {"title": "3주차 복습 퀴즈", "description": "NumPy 심화 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "NumPy 실전 프로젝트",
                "description": "NumPy를 활용한 미니 프로젝트 수행",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "프로젝트 소개", "description": "주식 데이터 분석 미니 프로젝트 개요 및 데이터 확인", "checked": False},
                    {"title": "데이터 로드", "description": "CSV 파일에서 주가 데이터 NumPy 배열로 로드", "checked": False},
                    {"title": "기초 통계 계산", "description": "일일 수익률, 평균 수익률, 변동성(표준편차) 계산", "checked": False},
                    {"title": "이동평균 계산", "description": "5일, 20일 이동평균 계산 및 np.convolve 활용", "checked": False},
                    {"title": "최대 하락폭 분석", "description": "Maximum Drawdown 계산 알고리즘 구현", "checked": False},
                    {"title": "결과 정리", "description": "분석 결과를 배열로 정리하고 파일로 저장", "checked": False},
                    {"title": "1개월차 종합 정리", "description": "NumPy 학습 내용 총정리 및 복습", "checked": False},
                ],
            },
        ]
        create_weekly_tasks(db, month1_r2.id, month1_r2_weeks)

        # Month 2: Pandas 데이터 처리
        month2_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=2,
            title="Pandas 데이터 처리",
            description="Pandas DataFrame을 활용한 데이터 분석 및 전처리 기법을 학습합니다.",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month2_r2)
        db.flush()

        month2_r2_weeks = [
            {
                "title": "Pandas 기초",
                "description": "Series와 DataFrame 생성, 기본 조작법 학습",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Pandas 소개와 설치", "description": "Pandas 특징, 설치, import pandas as pd 컨벤션", "checked": False},
                    {"title": "Series 다루기", "description": "pd.Series() 생성, 인덱싱, 값/인덱스 속성, 연산", "checked": False},
                    {"title": "DataFrame 생성", "description": "딕셔너리, 리스트, CSV로 DataFrame 생성하기", "checked": False},
                    {"title": "기본 정보 확인", "description": "head(), tail(), info(), describe(), shape, dtypes", "checked": False},
                    {"title": "열 선택과 추가", "description": "df['col'], df[['col1','col2']], 새 열 추가/삭제", "checked": False},
                    {"title": "행 선택하기", "description": "loc[], iloc[] 인덱서로 행 선택, 조건부 선택", "checked": False},
                    {"title": "1주차 복습 퀴즈", "description": "Pandas 기초 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "데이터 전처리",
                "description": "결측치 처리, 중복 제거, 데이터 타입 변환",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "결측치 확인", "description": "isnull(), notnull(), 결측치 개수 확인, 시각화", "checked": False},
                    {"title": "결측치 처리", "description": "dropna(), fillna() 메서드, 평균/중앙값 대체", "checked": False},
                    {"title": "중복 데이터 처리", "description": "duplicated(), drop_duplicates() 중복 확인 및 제거", "checked": False},
                    {"title": "데이터 타입 변환", "description": "astype(), to_datetime(), to_numeric() 형변환", "checked": False},
                    {"title": "문자열 처리", "description": "str 접근자, split(), replace(), contains() 활용", "checked": False},
                    {"title": "이상치 탐지", "description": "IQR 방식, Z-score로 이상치 탐지 및 처리", "checked": False},
                    {"title": "2주차 복습 퀴즈", "description": "데이터 전처리 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "데이터 집계와 그룹화",
                "description": "groupby, pivot_table을 활용한 데이터 집계",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "기본 집계 함수", "description": "sum(), mean(), count(), min(), max(), agg() 메서드", "checked": False},
                    {"title": "groupby 기초", "description": "그룹화 개념, 단일/복수 열 기준 groupby", "checked": False},
                    {"title": "그룹별 집계", "description": "그룹별 합계, 평균, 커스텀 집계 함수 적용", "checked": False},
                    {"title": "pivot_table 활용", "description": "피벗 테이블 생성, values, index, columns, aggfunc", "checked": False},
                    {"title": "crosstab 분석", "description": "pd.crosstab()으로 교차표 생성, 정규화 옵션", "checked": False},
                    {"title": "윈도우 함수", "description": "rolling(), expanding(), shift() 시계열 윈도우 함수", "checked": False},
                    {"title": "3주차 복습 퀴즈", "description": "데이터 집계 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "데이터 병합과 변형",
                "description": "merge, concat, melt를 활용한 데이터 조작",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "concat으로 연결", "description": "pd.concat() 세로/가로 연결, ignore_index 옵션", "checked": False},
                    {"title": "merge 기초", "description": "pd.merge() inner/left/right/outer join, on 키 지정", "checked": False},
                    {"title": "merge 심화", "description": "여러 키로 병합, suffixes 처리, indicator 옵션", "checked": False},
                    {"title": "melt로 변형", "description": "wide → long 형태 변환, id_vars, value_vars", "checked": False},
                    {"title": "pivot으로 변형", "description": "long → wide 형태 변환, pivot() vs pivot_table()", "checked": False},
                    {"title": "apply 함수 활용", "description": "apply()로 행/열별 사용자 정의 함수 적용", "checked": False},
                    {"title": "2개월차 종합 정리", "description": "Pandas 학습 내용 총정리 및 종합 프로젝트 계획", "checked": False},
                ],
            },
        ]
        create_weekly_tasks(db, month2_r2.id, month2_r2_weeks)

        # Month 3: 데이터 시각화
        month3_r2 = MonthlyGoal(
            id=uuid.uuid4(),
            roadmap_id=roadmap2.id,
            month_number=3,
            title="데이터 시각화",
            description="Matplotlib과 Seaborn을 활용하여 데이터를 효과적으로 시각화하는 방법을 학습합니다.",
            status=TaskStatus.PENDING,
            progress=0,
        )
        db.add(month3_r2)
        db.flush()

        month3_r2_weeks = [
            {
                "title": "Matplotlib 기초",
                "description": "기본 차트 종류와 스타일링 방법 학습",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Matplotlib 소개", "description": "설치, import matplotlib.pyplot as plt, 기본 구조", "checked": False},
                    {"title": "선 그래프", "description": "plot()으로 선 그래프 그리기, 선 스타일, 마커", "checked": False},
                    {"title": "막대 그래프", "description": "bar(), barh() 막대 그래프, 색상, 라벨 지정", "checked": False},
                    {"title": "히스토그램", "description": "hist()로 분포 시각화, bins 설정, density 옵션", "checked": False},
                    {"title": "산점도", "description": "scatter()로 두 변수 관계 시각화, 크기, 색상 매핑", "checked": False},
                    {"title": "차트 꾸미기", "description": "title, xlabel, ylabel, legend, grid 설정", "checked": False},
                    {"title": "1주차 복습 퀴즈", "description": "Matplotlib 기초 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "Matplotlib 심화",
                "description": "서브플롯, 다양한 차트 유형, 고급 설정",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Figure와 Axes", "description": "fig, ax = plt.subplots() 객체 지향 방식 이해", "checked": False},
                    {"title": "서브플롯 배치", "description": "여러 차트 배치, gridspec, 불규칙 레이아웃", "checked": False},
                    {"title": "파이 차트", "description": "pie()로 비율 시각화, explode, autopct 설정", "checked": False},
                    {"title": "박스플롯", "description": "boxplot()으로 분포와 이상치 시각화", "checked": False},
                    {"title": "스타일 설정", "description": "plt.style.use(), rcParams 전역 설정", "checked": False},
                    {"title": "이미지 저장", "description": "savefig()로 PNG, PDF, SVG 저장, DPI 설정", "checked": False},
                    {"title": "2주차 복습 퀴즈", "description": "Matplotlib 심화 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "Seaborn 시각화",
                "description": "통계 시각화에 특화된 Seaborn 라이브러리 학습",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "Seaborn 소개", "description": "설치, import seaborn as sns, 내장 데이터셋", "checked": False},
                    {"title": "분포 시각화", "description": "histplot(), kdeplot(), rugplot() 분포 표현", "checked": False},
                    {"title": "범주형 시각화", "description": "countplot(), barplot(), boxplot(), violinplot()", "checked": False},
                    {"title": "관계 시각화", "description": "scatterplot(), lineplot(), regplot() 회귀선", "checked": False},
                    {"title": "히트맵", "description": "heatmap()으로 상관관계, 피벗 테이블 시각화", "checked": False},
                    {"title": "FacetGrid", "description": "FacetGrid로 조건별 다중 차트 그리기", "checked": False},
                    {"title": "3주차 복습 퀴즈", "description": "Seaborn 내용 복습 및 퀴즈 풀이", "checked": False},
                ],
            },
            {
                "title": "종합 프로젝트",
                "description": "실제 데이터셋으로 EDA 프로젝트 수행",
                "status": TaskStatus.PENDING,
                "progress": 0,
                "days": [
                    {"title": "프로젝트 소개", "description": "타이타닉 생존자 분석 프로젝트 개요", "checked": False},
                    {"title": "데이터 로드 및 탐색", "description": "CSV 로드, 기본 정보 확인, 결측치 파악", "checked": False},
                    {"title": "데이터 전처리", "description": "결측치 처리, 범주형 변수 인코딩, 파생변수 생성", "checked": False},
                    {"title": "생존율 분석", "description": "성별, 객실등급, 나이별 생존율 시각화", "checked": False},
                    {"title": "상관관계 분석", "description": "변수 간 상관관계 히트맵, 주요 특성 파악", "checked": False},
                    {"title": "인사이트 정리", "description": "분석 결과 요약, 주요 발견사항 정리", "checked": False},
                    {"title": "전체 과정 회고", "description": "3개월 학습 회고, 다음 학습 방향 설정", "checked": False},
                ],
            },
        ]
        create_weekly_tasks(db, month3_r2.id, month3_r2_weeks)

        # ================================================================
        # ROADMAP 3: Completed - Git & GitHub 마스터 (1개월)
        # ================================================================
        roadmap3 = Roadmap(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Git & GitHub 마스터",
            description="Git 버전 관리의 기초부터 GitHub를 활용한 협업 워크플로우까지 학습합니다. 브랜치 전략, PR 리뷰, 충돌 해결 등 실무에서 필요한 기술을 익힙니다.",
            topic="Git GitHub 버전관리",
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
            description="Git 설치부터 브랜치, PR, 협업 워크플로우까지 전 과정 학습",
            status=TaskStatus.COMPLETED,
            progress=100,
        )
        db.add(month1_r3)
        db.flush()

        month1_r3_weeks = [
            {
                "title": "Git 기초",
                "description": "Git 설치, 기본 명령어, 커밋 관리",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "Git 소개와 설치", "description": "버전 관리 개념, Git 설치, 초기 설정 (user.name, user.email)", "checked": True},
                    {"title": "저장소 생성", "description": "git init, git clone, .git 폴더 구조 이해", "checked": True},
                    {"title": "기본 워크플로우", "description": "git add, git commit, git status, git log 명령어", "checked": True},
                    {"title": "변경사항 관리", "description": "git diff, git restore, git reset 사용법", "checked": True},
                    {"title": ".gitignore 설정", "description": "무시할 파일/폴더 패턴 지정, 템플릿 활용", "checked": True},
                    {"title": "커밋 메시지 작성", "description": "좋은 커밋 메시지 작성법, Conventional Commits", "checked": True},
                    {"title": "1주차 복습", "description": "Git 기초 명령어 실습 및 복습", "checked": True},
                ],
            },
            {
                "title": "브랜치와 병합",
                "description": "브랜치 생성, 전환, 병합, 충돌 해결",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "브랜치 개념", "description": "브랜치란? HEAD, main(master) 브랜치 이해", "checked": True},
                    {"title": "브랜치 생성과 전환", "description": "git branch, git checkout, git switch 명령어", "checked": True},
                    {"title": "브랜치 병합", "description": "git merge, Fast-forward vs 3-way merge 이해", "checked": True},
                    {"title": "충돌 해결", "description": "merge conflict 발생 시 수동 해결 방법", "checked": True},
                    {"title": "브랜치 전략", "description": "Git Flow, GitHub Flow, Trunk-based 전략 비교", "checked": True},
                    {"title": "Rebase 기초", "description": "git rebase 개념, merge vs rebase 차이점", "checked": True},
                    {"title": "2주차 복습", "description": "브랜치 실습: feature 브랜치로 기능 개발 후 병합", "checked": True},
                ],
            },
            {
                "title": "GitHub 활용",
                "description": "원격 저장소, Push/Pull, Issue, PR 관리",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "GitHub 계정과 저장소", "description": "GitHub 가입, 저장소 생성, README.md 작성", "checked": True},
                    {"title": "원격 저장소 연결", "description": "git remote add, git push, git pull 명령어", "checked": True},
                    {"title": "SSH 키 설정", "description": "SSH 키 생성, GitHub에 등록, 인증 테스트", "checked": True},
                    {"title": "Issue 관리", "description": "이슈 생성, 라벨 지정, 마일스톤 활용", "checked": True},
                    {"title": "Pull Request 생성", "description": "PR 생성, 설명 작성, 리뷰어 지정 방법", "checked": True},
                    {"title": "코드 리뷰", "description": "PR 리뷰 방법, 코멘트 작성, approve/request changes", "checked": True},
                    {"title": "3주차 복습", "description": "GitHub 워크플로우 전체 실습", "checked": True},
                ],
            },
            {
                "title": "협업 워크플로우",
                "description": "팀 협업 시나리오, Actions, 프로젝트 관리",
                "status": TaskStatus.COMPLETED,
                "progress": 100,
                "days": [
                    {"title": "Fork와 기여", "description": "오픈소스 기여 워크플로우, fork → PR 과정", "checked": True},
                    {"title": "GitHub Actions 기초", "description": "CI/CD 개념, workflow 파일 작성 기초", "checked": True},
                    {"title": "자동화 워크플로우", "description": "테스트 자동화, 린트 검사 워크플로우 설정", "checked": True},
                    {"title": "GitHub Projects", "description": "칸반 보드 생성, 이슈 연결, 진행상황 관리", "checked": True},
                    {"title": "팀 협업 시나리오", "description": "실제 팀 협업 상황 시뮬레이션 실습", "checked": True},
                    {"title": "Git 고급 기능", "description": "stash, cherry-pick, reflog, bisect 명령어", "checked": True},
                    {"title": "전체 과정 정리", "description": "Git & GitHub 학습 내용 총정리 및 회고", "checked": True},
                ],
            },
        ]
        create_weekly_tasks(db, month1_r3.id, month1_r3_weeks)

        db.commit()
        print("\n✅ Mock data seeded successfully!")
        print(f"Created 3 roadmaps for user {user.email}:")
        print("  1. React 포트폴리오 프로젝트 (Planning, 2개월, 진행중)")
        print("  2. Python 데이터 분석 마스터 (Learning, 3개월, 진행중)")
        print("  3. Git & GitHub 마스터 (Learning, 1개월, 완료)")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_mock_data()
