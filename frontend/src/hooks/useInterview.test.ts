import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createElement } from 'react';
import {
  useInterviewSessions,
  useInterviewSession,
  useInterviewQuestions,
  useStartInterview,
  useSubmitInterviewAnswers,
  useAbandonInterview,
  useDeleteInterview,
  useGenerateRoadmapFromInterview,
} from './useInterview';
import { interviewApi } from '@/lib/api';

// Mock the API module
vi.mock('@/lib/api', () => ({
  interviewApi: {
    list: vi.fn(),
    get: vi.fn(),
    getQuestions: vi.fn(),
    start: vi.fn(),
    submitAnswers: vi.fn(),
    abandon: vi.fn(),
    delete: vi.fn(),
    generateRoadmap: vi.fn(),
  },
}));

const mockedInterviewApi = vi.mocked(interviewApi);

// Create wrapper component for tests
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('useInterviewSessions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches interview sessions successfully', async () => {
    const mockSessions = {
      sessions: [
        {
          id: 'session-1',
          topic: 'Python',
          status: 'in_progress',
          current_stage: 1,
        },
        {
          id: 'session-2',
          topic: 'React',
          status: 'completed',
          current_stage: 3,
        },
      ],
      total: 2,
    };

    mockedInterviewApi.list.mockResolvedValueOnce({ data: mockSessions });

    const { result } = renderHook(() => useInterviewSessions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockSessions);
    expect(mockedInterviewApi.list).toHaveBeenCalledWith(undefined);
  });

  it('passes filter params correctly', async () => {
    mockedInterviewApi.list.mockResolvedValueOnce({
      data: { sessions: [], total: 0 },
    });

    const { result } = renderHook(
      () => useInterviewSessions({ status_filter: 'completed', limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockedInterviewApi.list).toHaveBeenCalledWith({
      status_filter: 'completed',
      limit: 10,
    });
  });
});

describe('useInterviewSession', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches single interview session', async () => {
    const mockSession = {
      id: 'session-1',
      topic: 'Python',
      status: 'in_progress',
      current_stage: 2,
    };

    mockedInterviewApi.get.mockResolvedValueOnce({ data: mockSession });

    const { result } = renderHook(() => useInterviewSession('session-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockSession);
    expect(mockedInterviewApi.get).toHaveBeenCalledWith('session-1');
  });

  it('does not fetch when sessionId is empty', () => {
    renderHook(() => useInterviewSession(''), {
      wrapper: createWrapper(),
    });

    expect(mockedInterviewApi.get).not.toHaveBeenCalled();
  });
});

describe('useInterviewQuestions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches current questions for session', async () => {
    const mockQuestions = {
      session_id: 'session-1',
      current_stage: 1,
      stage_name: '목표 구체화',
      questions: [
        { id: 'q1', question: '목표는?', question_type: 'text' },
      ],
      is_complete: false,
      is_followup: false,
    };

    mockedInterviewApi.getQuestions.mockResolvedValueOnce({ data: mockQuestions });

    const { result } = renderHook(() => useInterviewQuestions('session-1'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockQuestions);
  });
});

describe('useStartInterview', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('starts a new interview', async () => {
    const mockResponse = {
      session_id: 'new-session',
      questions: [
        { id: 'q1', question: '목표는?', question_type: 'text' },
      ],
    };

    mockedInterviewApi.start.mockResolvedValueOnce({ data: mockResponse });

    const { result } = renderHook(() => useStartInterview(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync({
      topic: 'Python',
      mode: 'learning',
      duration_months: 3,
    });

    expect(mockedInterviewApi.start).toHaveBeenCalledWith({
      topic: 'Python',
      mode: 'learning',
      duration_months: 3,
    });
  });
});

describe('useSubmitInterviewAnswers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('submits answers for session', async () => {
    const mockResponse = {
      session_id: 'session-1',
      is_complete: false,
      questions: [
        { id: 'q2', question: '다음 질문', question_type: 'text' },
      ],
    };

    mockedInterviewApi.submitAnswers.mockResolvedValueOnce({ data: mockResponse });

    const { result } = renderHook(() => useSubmitInterviewAnswers('session-1'), {
      wrapper: createWrapper(),
    });

    const answers = [
      { question_id: 'q1', answer: '웹 개발을 배우고 싶습니다' },
    ];

    await result.current.mutateAsync(answers);

    expect(mockedInterviewApi.submitAnswers).toHaveBeenCalledWith('session-1', answers);
  });
});

describe('useAbandonInterview', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('abandons an interview session', async () => {
    const mockResponse = {
      id: 'session-1',
      status: 'abandoned',
    };

    mockedInterviewApi.abandon.mockResolvedValueOnce({ data: mockResponse });

    const { result } = renderHook(() => useAbandonInterview(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync('session-1');

    expect(mockedInterviewApi.abandon).toHaveBeenCalledWith('session-1');
  });
});

describe('useDeleteInterview', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deletes an interview session', async () => {
    mockedInterviewApi.delete.mockResolvedValueOnce({ data: {} });

    const { result } = renderHook(() => useDeleteInterview(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync('session-1');

    expect(mockedInterviewApi.delete).toHaveBeenCalledWith('session-1');
  });
});

describe('useGenerateRoadmapFromInterview', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('generates roadmap from completed interview', async () => {
    const mockResponse = {
      roadmap_id: 'new-roadmap-id',
      message: 'Roadmap generated successfully',
    };

    mockedInterviewApi.generateRoadmap.mockResolvedValueOnce({ data: mockResponse });

    const { result } = renderHook(() => useGenerateRoadmapFromInterview(), {
      wrapper: createWrapper(),
    });

    await result.current.mutateAsync({
      interview_session_id: 'session-1',
      start_date: '2024-01-15',
      use_web_search: true,
    });

    expect(mockedInterviewApi.generateRoadmap).toHaveBeenCalledWith({
      interview_session_id: 'session-1',
      start_date: '2024-01-15',
      use_web_search: true,
    });
  });
});
