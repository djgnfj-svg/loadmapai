import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@/test/test-utils';
import userEvent from '@testing-library/user-event';
import { DeepInterviewStep, InterviewCompleted } from './DeepInterviewStep';
import type { InterviewQuestionsResponse, InterviewCompletedResponse } from '@/types';

describe('DeepInterviewStep', () => {
  const mockOnSubmitAnswers = vi.fn();

  const mockQuestionsData: InterviewQuestionsResponse = {
    session_id: 'test-session-id',
    current_round: 1,
    max_rounds: 3,
    questions: [
      {
        id: 'q1',
        question: '어떤 목표를 이루고 싶으신가요?',
        question_type: 'text',
        placeholder: '구체적인 목표를 입력하세요',
      },
      {
        id: 'q2',
        question: '현재 경험 수준은?',
        question_type: 'single_choice',
        options: ['초급', '중급', '고급'],
      },
    ],
    is_complete: false,
    is_followup: false,
  };

  beforeEach(() => {
    mockOnSubmitAnswers.mockClear();
  });

  it('renders loading state', () => {
    render(
      <DeepInterviewStep
        questionsData={null}
        isLoading={true}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('AI가 맞춤 질문을 생성 중입니다')).toBeInTheDocument();
  });

  it('renders error state', () => {
    render(
      <DeepInterviewStep
        questionsData={null}
        isLoading={false}
        error="인터뷰 시작 중 오류가 발생했습니다"
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('오류가 발생했습니다')).toBeInTheDocument();
    expect(screen.getByText('인터뷰 시작 중 오류가 발생했습니다')).toBeInTheDocument();
  });

  it('renders questions correctly', () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('어떤 목표를 이루고 싶으신가요?')).toBeInTheDocument();
    expect(screen.getByText('현재 경험 수준은?')).toBeInTheDocument();
    expect(screen.getByText('초급')).toBeInTheDocument();
    expect(screen.getByText('중급')).toBeInTheDocument();
    expect(screen.getByText('고급')).toBeInTheDocument();
  });

  it('allows text input for text questions', async () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    const textArea = screen.getByPlaceholderText('구체적인 목표를 입력하세요');
    await userEvent.type(textArea, '프론트엔드 개발자가 되고 싶습니다');

    expect(textArea).toHaveValue('프론트엔드 개발자가 되고 싶습니다');
  });

  it('allows selecting options for choice questions', async () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    const optionButton = screen.getByText('중급');
    await userEvent.click(optionButton);

    // The selected option should have different styling
    expect(optionButton.closest('button')).toHaveClass('border-primary-500');
  });

  it('disables submit button when not all questions are answered', () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    const submitButton = screen.getByRole('button', { name: /완료/i });
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when all questions are answered', async () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    // Answer text question
    const textArea = screen.getByPlaceholderText('구체적인 목표를 입력하세요');
    await userEvent.type(textArea, '웹 개발을 배우고 싶습니다');

    // Answer choice question
    await userEvent.click(screen.getByText('초급'));

    const submitButton = screen.getByRole('button', { name: /완료/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('calls onSubmitAnswers with correct data', async () => {
    render(
      <DeepInterviewStep
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    // Answer questions
    await userEvent.type(
      screen.getByPlaceholderText('구체적인 목표를 입력하세요'),
      '프론트엔드 개발자'
    );
    await userEvent.click(screen.getByText('중급'));

    // Submit
    await userEvent.click(screen.getByRole('button', { name: /완료/i }));

    expect(mockOnSubmitAnswers).toHaveBeenCalledWith([
      { question_id: 'q1', answer: '프론트엔드 개발자' },
      { question_id: 'q2', answer: '중급' },
    ]);
  });

  it('shows followup state correctly', () => {
    const followupData: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      current_round: 2,
      is_followup: true,
      ambiguous_count: 1,
    };

    render(
      <DeepInterviewStep
        questionsData={followupData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('조금 더 자세히 알려주세요')).toBeInTheDocument();
    expect(screen.getByText(/추가 질문/)).toBeInTheDocument();
  });

  it('shows warning message when present', () => {
    const dataWithWarning: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      warning_message: '연속으로 불완전한 답변이 감지되었습니다',
    };

    render(
      <DeepInterviewStep
        questionsData={dataWithWarning}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('연속으로 불완전한 답변이 감지되었습니다')).toBeInTheDocument();
  });

  it('shows terminated state', () => {
    const terminatedData: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      is_terminated: true,
      termination_reason: '연속 3회 이상한 답변',
    };

    render(
      <DeepInterviewStep
        questionsData={terminatedData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('인터뷰가 종료되었습니다')).toBeInTheDocument();
    expect(screen.getByText('연속 3회 이상한 답변')).toBeInTheDocument();
  });

  it('shows retry indicator for retry questions', () => {
    const retryData: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      is_followup: true,
      questions: [
        {
          id: 'q1_followup',
          question: '다시 답변해 주세요: 어떤 목표를 이루고 싶으신가요?',
          question_type: 'text',
          is_retry: true,
          context: '이전에 "ㅋㅋ"라고 답변하셨는데...',
        },
      ],
    };

    render(
      <DeepInterviewStep
        questionsData={retryData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('(다시 답변해 주세요)')).toBeInTheDocument();
    expect(screen.getByText('이전에 "ㅋㅋ"라고 답변하셨는데...')).toBeInTheDocument();
  });
});

describe('InterviewCompleted', () => {
  const mockOnGenerateRoadmap = vi.fn();

  const mockCompletedData: InterviewCompletedResponse = {
    session_id: 'test-session-id',
    is_complete: true,
    compiled_context: '사용자는 프론트엔드 개발자가 되길 원합니다...',
    key_insights: [
      '목표: 프론트엔드 개발자',
      '현재 수준: 초급',
      '학습 시간: 하루 2시간',
    ],
    schedule: {
      daily_minutes: 120,
      rest_days: [0, 6],
      intensity: 'moderate',
    },
    can_generate_roadmap: true,
  };

  beforeEach(() => {
    mockOnGenerateRoadmap.mockClear();
  });

  it('renders completion message', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    expect(screen.getByText('준비 완료!')).toBeInTheDocument();
  });

  it('renders key insights', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    expect(screen.getByText('핵심 인사이트')).toBeInTheDocument();
    expect(screen.getByText('목표: 프론트엔드 개발자')).toBeInTheDocument();
    expect(screen.getByText('현재 수준: 초급')).toBeInTheDocument();
    expect(screen.getByText('학습 시간: 하루 2시간')).toBeInTheDocument();
  });

  it('renders schedule summary', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    expect(screen.getByText('학습 스케줄')).toBeInTheDocument();
    expect(screen.getByText('120분')).toBeInTheDocument();
    expect(screen.getByText('하루 학습')).toBeInTheDocument();
  });

  it('calls onGenerateRoadmap when button is clicked', async () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    await userEvent.click(screen.getByText('맞춤형 로드맵 생성하기'));

    expect(mockOnGenerateRoadmap).toHaveBeenCalledTimes(1);
  });

  it('shows loading state while generating', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={true}
      />
    );

    expect(screen.getByText('로드맵 생성 중...')).toBeInTheDocument();
  });

  it('disables button while generating', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={true}
      />
    );

    const button = screen.getByRole('button', { name: /로드맵 생성 중/i });
    expect(button).toBeDisabled();
  });

  it('displays intensity correctly', () => {
    render(
      <InterviewCompleted
        data={mockCompletedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    expect(screen.getByText('균형있게')).toBeInTheDocument();
  });

  it('shows forced completion notice', () => {
    const forcedData: InterviewCompletedResponse = {
      ...mockCompletedData,
      forced_completion: true,
    };

    render(
      <InterviewCompleted
        data={forcedData}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    expect(screen.getByText('정보 수집 완료')).toBeInTheDocument();
    expect(screen.getByText(/일부 정보가 불완전하여/)).toBeInTheDocument();
  });

  it('handles missing insights gracefully', () => {
    const dataWithoutInsights: InterviewCompletedResponse = {
      ...mockCompletedData,
      key_insights: [],
    };

    render(
      <InterviewCompleted
        data={dataWithoutInsights}
        onGenerateRoadmap={mockOnGenerateRoadmap}
        isGenerating={false}
      />
    );

    // Should not show insights section when empty
    expect(screen.queryByText('핵심 인사이트')).not.toBeInTheDocument();
  });
});
