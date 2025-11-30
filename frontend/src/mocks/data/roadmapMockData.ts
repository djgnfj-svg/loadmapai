import type { InterviewQuestion } from '../../types';

// ============ Mock Questions ============

export const mockQuestions: InterviewQuestion[] = [
  {
    id: 'q1',
    question: '현재 관련 지식이나 경험이 있으신가요?',
    question_type: 'single_choice',
    options: ['없음 (완전 초보)', '조금 있음', '중급', '고급'],
  },
  {
    id: 'q2',
    question: '하루에 얼마나 시간을 투자할 수 있나요?',
    question_type: 'single_choice',
    options: ['30분 이하', '1시간', '2시간', '3시간 이상'],
  },
  {
    id: 'q3',
    question: '구체적으로 달성하고 싶은 목표가 있나요?',
    question_type: 'text',
    placeholder: '예: 토이 프로젝트 완성, 취업 등',
  },
  {
    id: 'q4',
    question: '선호하는 학습 방식이 있나요?',
    question_type: 'single_choice',
    options: ['동영상 강의', '책/문서', '실습 위주', '혼합'],
  },
];

// ============ Mock Interview SSE Events ============

export const mockInterviewStartSSE = [
  { delay: 100, data: { type: 'start', message: '인터뷰를 시작합니다...', progress: 0 } },
  { delay: 200, data: { type: 'progress', message: '질문 생성 중...', progress: 30 } },
  { delay: 300, data: { type: 'progress', message: '질문 준비 완료', progress: 70 } },
];
