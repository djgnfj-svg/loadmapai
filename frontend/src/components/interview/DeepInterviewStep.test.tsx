import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import userEvent from '@testing-library/user-event';
import { DeepInterviewStep, InterviewCompleted } from './DeepInterviewStep';
import type { InterviewQuestionsResponse, InterviewCompletedResponse } from '@/types';

describe('DeepInterviewStep', () => {
  const mockOnSubmitAnswers = vi.fn();

  const mockQuestionsData: InterviewQuestionsResponse = {
    session_id: 'test-session-id',
    current_stage: 1,
    stage_name: '목표 구체화',
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
        sessionId="test-session"
        questionsData={null}
        isLoading={true}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('AI가 질문을 준비 중입니다')).toBeInTheDocument();
  });

  it('renders error state', () => {
    render(
      <DeepInterviewStep
        sessionId="test-session"
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
        sessionId="test-session"
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

  it('renders stage progress indicator', () => {
    render(
      <DeepInterviewStep
        sessionId="test-session"
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    // Should show 3 stage indicators
    const stageIndicators = screen.getAllByText(/[123]/);
    expect(stageIndicators.length).toBeGreaterThanOrEqual(1);
  });

  it('allows text input for text questions', async () => {
    render(
      <DeepInterviewStep
        sessionId="test-session"
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
        sessionId="test-session"
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
        sessionId="test-session"
        questionsData={mockQuestionsData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    const submitButton = screen.getByRole('button', { name: /다음 단계로|인터뷰 완료/i });
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when all questions are answered', async () => {
    render(
      <DeepInterviewStep
        sessionId="test-session"
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

    const submitButton = screen.getByRole('button', { name: /다음 단계로|인터뷰 완료/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('calls onSubmitAnswers with correct data', async () => {
    render(
      <DeepInterviewStep
        sessionId="test-session"
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
    await userEvent.click(screen.getByRole('button', { name: /다음 단계로/i }));

    expect(mockOnSubmitAnswers).toHaveBeenCalledWith([
      { question_id: 'q1', answer: '프론트엔드 개발자' },
      { question_id: 'q2', answer: '중급' },
    ]);
  });

  it('shows followup state correctly', () => {
    const followupData: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      is_followup: true,
    };

    render(
      <DeepInterviewStep
        sessionId="test-session"
        questionsData={followupData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByText('조금 더 구체적으로 알려주세요')).toBeInTheDocument();
    expect(screen.getByText('추가 질문')).toBeInTheDocument();
  });

  it('shows correct button text for final stage', () => {
    const finalStageData: InterviewQuestionsResponse = {
      ...mockQuestionsData,
      current_stage: 3,
      stage_name: '제약 조건',
    };

    render(
      <DeepInterviewStep
        sessionId="test-session"
        questionsData={finalStageData}
        isLoading={false}
        error={null}
        onSubmitAnswers={mockOnSubmitAnswers}
        isSubmitting={false}
      />
    );

    expect(screen.getByRole('button', { name: /인터뷰 완료/i })).toBeInTheDocument();
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

    expect(screen.getByText('인터뷰가 완료되었습니다!')).toBeInTheDocument();
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
