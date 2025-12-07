import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';
import type { DailyFeedback } from '@/types';

interface DailyFeedbackViewProps {
  feedback: DailyFeedback;
  onViewWrongQuestions?: () => void;
  onNextDay?: () => void;
  showActions?: boolean;
}

export function DailyFeedbackView({
  feedback,
  onViewWrongQuestions,
  onNextDay,
  showActions = true,
}: DailyFeedbackViewProps) {
  const accuracyPercent = Math.round(feedback.accuracy_rate * 100);

  return (
    <Card variant="elevated" className="overflow-hidden">
      {/* Header with result */}
      <div
        className={cn(
          'p-6 text-center',
          feedback.is_passed
            ? 'bg-gradient-to-r from-green-500 to-emerald-500'
            : 'bg-gradient-to-r from-orange-500 to-amber-500'
        )}
      >
        <div className="text-white mb-2">
          {feedback.is_passed ? (
            <svg
              className="w-16 h-16 mx-auto mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          ) : (
            <svg
              className="w-16 h-16 mx-auto mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
          <h2 className="text-2xl font-bold">
            {feedback.is_passed ? '학습 완료!' : '조금 더 노력해봐요!'}
          </h2>
        </div>

        {/* Accuracy Circle */}
        <div className="relative inline-flex items-center justify-center w-32 h-32 mt-4">
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="rgba(255,255,255,0.3)"
              strokeWidth="12"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="white"
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${(accuracyPercent / 100) * 352} 352`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute text-white">
            <div className="text-3xl font-bold">{accuracyPercent}%</div>
            <div className="text-sm opacity-80">정답률</div>
          </div>
        </div>

        <div className="text-white/90 mt-4">
          <span className="text-xl font-semibold">
            {feedback.correct_count} / {feedback.total_questions}
          </span>
          <span className="text-sm ml-2">문제 정답</span>
        </div>
      </div>

      <CardContent className="p-6">
        {/* Summary */}
        <div className="mb-6">
          <p className="text-gray-700 dark:text-gray-300 text-lg">
            {feedback.summary}
          </p>
        </div>

        {/* Strengths */}
        {feedback.strengths && feedback.strengths.length > 0 && (
          <div className="mb-4">
            <h4 className="flex items-center gap-2 text-sm font-semibold text-green-600 dark:text-green-400 mb-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              잘한 점
            </h4>
            <ul className="space-y-1">
              {feedback.strengths.map((strength, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <span className="text-green-500 mt-0.5">+</span>
                  {strength}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Improvements */}
        {feedback.improvements && feedback.improvements.length > 0 && (
          <div className="mb-6">
            <h4 className="flex items-center gap-2 text-sm font-semibold text-orange-600 dark:text-orange-400 mb-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              개선할 점
            </h4>
            <ul className="space-y-1">
              {feedback.improvements.map((improvement, index) => (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
                >
                  <span className="text-orange-500 mt-0.5">!</span>
                  {improvement}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="flex flex-col sm:flex-row gap-3 mt-6 pt-4 border-t border-gray-100 dark:border-dark-700">
            {!feedback.is_passed && onViewWrongQuestions && (
              <Button variant="outline" onClick={onViewWrongQuestions} fullWidth>
                틀린 문제 다시 보기
              </Button>
            )}
            {feedback.is_passed && onNextDay && (
              <Button onClick={onNextDay} fullWidth>
                다음 일차로 이동
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
