import { useState, useMemo } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';
import { QuestionCard } from './QuestionCard';
import { DailyFeedbackView } from './DailyFeedbackView';
import {
  useQuestions,
  useSubmitAnswer,
  useCompleteDay,
  useLearningDayInfo,
} from '@/hooks/useLearning';
import type { DailyFeedback } from '@/types';

interface LearningDayViewProps {
  dailyTaskId: string;
  weeklyTaskId: string;
  dayNumber: number;
  title: string;
  onNextDay?: () => void;
}

export function LearningDayView({
  dailyTaskId,
  weeklyTaskId,
  dayNumber,
  title,
  onNextDay,
}: LearningDayViewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState<DailyFeedback | null>(null);

  const { data: questions, isLoading, refetch } = useQuestions(dailyTaskId);
  const { data: dayInfo } = useLearningDayInfo(dailyTaskId);
  const submitAnswerMutation = useSubmitAnswer(dailyTaskId);
  const completeDayMutation = useCompleteDay(dailyTaskId, weeklyTaskId);

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

  // Show feedback if already completed
  if (dayInfo?.is_completed && dayInfo?.feedback && !showFeedback) {
    return (
      <DailyFeedbackView
        feedback={dayInfo.feedback}
        onNextDay={onNextDay}
        showActions={true}
      />
    );
  }

  if (showFeedback && feedback) {
    return (
      <DailyFeedbackView
        feedback={feedback}
        onNextDay={onNextDay}
        onViewWrongQuestions={() => setShowFeedback(false)}
        showActions={true}
      />
    );
  }

  if (isLoading) {
    return (
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
    );
  }

  if (!questions || questions.length === 0) {
    return (
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
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card variant="bordered" padding="sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Day {dayNumber}: {title}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              진행률: {progress.answered} / {progress.total} 문제 답변 완료
            </p>
          </div>

          {/* Progress Bar */}
          <div className="flex items-center gap-4">
            <div className="w-32 h-2 bg-gray-200 dark:bg-dark-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-300"
                style={{ width: `${progress.percent}%` }}
              />
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {progress.percent}%
            </span>
          </div>
        </div>
      </Card>

      {/* Question Navigation */}
      <div className="flex flex-wrap gap-2 justify-center">
        {questions.map((q, index) => {
          const isAnswered = !!q.user_answer;
          const isCurrent = index === currentIndex;

          return (
            <button
              key={q.id}
              onClick={() => goToQuestion(index)}
              className={cn(
                'w-10 h-10 rounded-lg font-medium text-sm transition-all',
                isCurrent && 'ring-2 ring-primary-500 ring-offset-2 dark:ring-offset-dark-900',
                isAnswered && !isCurrent && 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
                !isAnswered && !isCurrent && 'bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-400',
                isCurrent && 'bg-primary-500 text-white'
              )}
            >
              {index + 1}
            </button>
          );
        })}
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
      <div className="flex justify-between items-center">
        <Button
          variant="ghost"
          onClick={() => goToQuestion(currentIndex - 1)}
          disabled={currentIndex === 0}
        >
          <svg
            className="w-5 h-5 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          이전
        </Button>

        {currentIndex === totalQuestions - 1 ? (
          <Button
            onClick={handleCompleteDay}
            disabled={progress.answered < progress.total || completeDayMutation.isPending}
            isLoading={completeDayMutation.isPending}
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
        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          모든 문제에 답변을 완료해야 제출할 수 있습니다.
        </p>
      )}
    </div>
  );
}
