import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Progress } from '@/components/common/Progress';
import { QuestionCard, DailyFeedbackView } from '@/components/learning';
import {
  useQuestions,
  useSubmitAnswer,
  useCompleteDay,
  useLearningDayInfo,
} from '@/hooks/useLearning';
import { cn } from '@/lib/utils';
import type { DailyFeedback } from '@/types';

export function LearningPage() {
  const { id: roadmapId, dailyTaskId } = useParams<{ id: string; dailyTaskId: string }>();
  const navigate = useNavigate();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState<DailyFeedback | null>(null);

  const { data: questions, isLoading, refetch } = useQuestions(dailyTaskId || '');
  const { data: dayInfo } = useLearningDayInfo(dailyTaskId || '');
  const submitAnswerMutation = useSubmitAnswer(dailyTaskId);
  const completeDayMutation = useCompleteDay(dailyTaskId || '', dayInfo?.weekly_task_id);

  const totalQuestions = questions?.length || 0;
  const currentQuestion = questions?.[currentIndex];

  const progress = useMemo(() => {
    if (!questions) return { answered: 0, total: 0, percent: 0 };
    const answered = questions.filter((q) => q.user_answer).length;
    return {
      answered,
      total: questions.length,
      percent: questions.length > 0 ? Math.round((answered / questions.length) * 100) : 0,
    };
  }, [questions]);

  const handleAnswerChange = (_answer: string) => {
    // Answer is tracked locally in QuestionCard
  };

  const handleSubmitAnswer = async (questionId: string, answerText: string) => {
    await submitAnswerMutation.mutateAsync({ questionId, answerText });
  };

  const handleCompleteDay = async () => {
    const result = await completeDayMutation.mutateAsync();
    setFeedback(result.data.feedback);
    setShowFeedback(true);
    refetch();
  };

  const goToQuestion = (index: number) => {
    if (index >= 0 && index < totalQuestions) {
      setCurrentIndex(index);
    }
  };

  const handleBackToRoadmap = () => {
    navigate(`/roadmaps/${roadmapId}`);
  };

  // Show feedback if already completed
  if (dayInfo?.is_completed && dayInfo?.feedback && !showFeedback) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <Button
          variant="ghost"
          onClick={handleBackToRoadmap}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          로드맵으로 돌아가기
        </Button>
        <DailyFeedbackView
          feedback={dayInfo.feedback}
          onNextDay={handleBackToRoadmap}
          showActions={true}
        />
      </div>
    );
  }

  // Show feedback after completion
  if (showFeedback && feedback) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <DailyFeedbackView
          feedback={feedback}
          onNextDay={handleBackToRoadmap}
          onViewWrongQuestions={() => setShowFeedback(false)}
          showActions={true}
        />
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <Card variant="elevated" className="p-8">
          <div className="flex items-center justify-center">
            <svg
              className="animate-spin h-8 w-8 text-primary-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span className="ml-3 text-gray-600 dark:text-gray-400">
              문제를 불러오는 중...
            </span>
          </div>
        </Card>
      </div>
    );
  }

  // No questions
  if (!questions || questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <Button
          variant="ghost"
          onClick={handleBackToRoadmap}
          className="mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          로드맵으로 돌아가기
        </Button>
        <Card variant="elevated" className="p-8 text-center">
          <svg
            className="w-16 h-16 mx-auto text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
            문제가 없습니다
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            이 일차에는 아직 문제가 생성되지 않았습니다.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={handleBackToRoadmap}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          로드맵으로 돌아가기
        </Button>

        <Card variant="bordered" padding="md">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Day {dayInfo?.day_number}: {dayInfo?.title || '학습'}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {progress.answered} / {progress.total} 문제 답변 완료
              </p>
            </div>

            {/* Progress */}
            <div className="flex items-center gap-4">
              <div className="w-40">
                <Progress value={progress.percent} size="md" color="primary" />
              </div>
              <span className="text-lg font-semibold text-primary-600 dark:text-primary-400">
                {progress.percent}%
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Question Navigation Grid */}
      <div className="mb-6">
        <Card variant="bordered" padding="sm">
          <div className="flex flex-wrap gap-2 justify-center py-2">
            {questions.map((q, index) => {
              const isAnswered = !!q.user_answer;
              const isCurrent = index === currentIndex;
              const isCorrect = q.user_answer?.is_correct;
              const isGraded = q.user_answer?.is_correct !== undefined && q.user_answer?.is_correct !== null;

              return (
                <button
                  key={q.id}
                  onClick={() => goToQuestion(index)}
                  className={cn(
                    'w-11 h-11 rounded-xl font-medium text-sm transition-all relative',
                    'flex items-center justify-center',
                    isCurrent && 'ring-2 ring-primary-500 ring-offset-2 dark:ring-offset-dark-900',
                    isAnswered && !isCurrent && !isGraded && 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
                    isGraded && isCorrect && 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
                    isGraded && !isCorrect && 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
                    !isAnswered && !isCurrent && 'bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-400',
                    isCurrent && 'bg-primary-500 text-white'
                  )}
                >
                  {index + 1}
                  {isGraded && (
                    <span className="absolute -top-1 -right-1">
                      {isCorrect ? (
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Current Question */}
      {currentQuestion && (
        <QuestionCard
          question={currentQuestion}
          questionNumber={currentIndex + 1}
          totalQuestions={totalQuestions}
          onAnswerChange={handleAnswerChange}
          onSubmit={(answer) => {
            if (answer.trim()) {
              handleSubmitAnswer(currentQuestion.id, answer);
            }
          }}
          isSubmitting={submitAnswerMutation.isPending}
        />
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center mt-6">
        <Button
          variant="ghost"
          onClick={() => goToQuestion(currentIndex - 1)}
          disabled={currentIndex === 0}
        >
          <ArrowLeft className="w-5 h-5 mr-1" />
          이전
        </Button>

        {currentIndex === totalQuestions - 1 ? (
          <Button
            onClick={handleCompleteDay}
            disabled={progress.answered < progress.total || completeDayMutation.isPending}
            isLoading={completeDayMutation.isPending}
            size="lg"
          >
            전체 제출하기
          </Button>
        ) : (
          <Button
            variant="secondary"
            onClick={() => goToQuestion(currentIndex + 1)}
          >
            다음
            <svg
              className="w-5 h-5 ml-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </Button>
        )}
      </div>

      {/* Submission Status */}
      {progress.answered < progress.total && (
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
          모든 문제에 답변을 완료해야 제출할 수 있습니다.
        </p>
      )}
    </div>
  );
}
