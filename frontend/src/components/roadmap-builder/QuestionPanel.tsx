import { useState } from 'react';
import { cn } from '../../lib/utils';
import type { InterviewQuestion } from '../../types';

interface QuestionPanelProps {
  questions: InterviewQuestion[];
  answers: Map<string, string>;
  onAnswerChange: (questionId: string, answer: string) => void;
  onAnswerSubmit: (questionId: string) => void;
  submittingQuestionId: string | null;
  currentQuestionIndex: number;
  className?: string;
}

export function QuestionPanel({
  questions,
  answers,
  onAnswerChange,
  onAnswerSubmit,
  submittingQuestionId,
  currentQuestionIndex,
  className,
}: QuestionPanelProps) {
  const progress = questions.length > 0
    ? Math.round((answers.size / questions.length) * 100)
    : 0;

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 헤더 */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI 인터뷰
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          질문에 답변하면 로드맵이 실시간으로 구체화됩니다
        </p>

        {/* 진행률 바 */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {answers.size} / {questions.length} 질문 완료
        </p>
      </div>

      {/* 질문 목록 */}
      <div className="flex-1 overflow-y-auto space-y-4">
        {questions.map((question, index) => (
          <QuestionCard
            key={question.id}
            question={question}
            index={index}
            answer={answers.get(question.id) || ''}
            onAnswerChange={(answer) => onAnswerChange(question.id, answer)}
            onSubmit={() => onAnswerSubmit(question.id)}
            isSubmitting={submittingQuestionId === question.id}
            isAnswered={answers.has(question.id)}
            isCurrent={index === currentQuestionIndex}
          />
        ))}
      </div>
    </div>
  );
}

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
  isAnswered: boolean;
  isCurrent: boolean;
}

function QuestionCard({
  question,
  index,
  answer,
  onAnswerChange,
  onSubmit,
  isSubmitting,
  isAnswered,
  isCurrent,
}: QuestionCardProps) {
  const [localAnswer, setLocalAnswer] = useState(answer);

  const handleSubmit = () => {
    if (localAnswer.trim() && !isSubmitting && !isAnswered) {
      onAnswerChange(localAnswer);
      onSubmit();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && question.question_type !== 'text') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border transition-all duration-200',
        isCurrent && !isAnswered
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400'
          : isAnswered
          ? 'border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-600'
          : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
      )}
    >
      {/* 질문 헤더 */}
      <div className="flex items-start gap-3 mb-3">
        <span
          className={cn(
            'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
            isAnswered
              ? 'bg-green-500 text-white'
              : isCurrent
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
          )}
        >
          {isAnswered ? '✓' : index + 1}
        </span>
        <p className="text-sm font-medium text-gray-900 dark:text-white">
          {question.question}
        </p>
      </div>

      {/* 답변 입력 */}
      {question.question_type === 'single_choice' && question.options ? (
        <div className="space-y-2 ml-9">
          {question.options.map((option) => (
            <button
              key={option}
              onClick={() => {
                if (!isAnswered && !isSubmitting) {
                  setLocalAnswer(option);
                  onAnswerChange(option);
                  onSubmit();
                }
              }}
              disabled={isAnswered || isSubmitting}
              className={cn(
                'w-full text-left px-3 py-2 rounded-md text-sm transition-all',
                localAnswer === option || answer === option
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600',
                (isAnswered || isSubmitting) && 'cursor-not-allowed opacity-60'
              )}
            >
              {option}
            </button>
          ))}
        </div>
      ) : (
        <div className="ml-9 space-y-2">
          <input
            type="text"
            value={localAnswer}
            onChange={(e) => setLocalAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={question.placeholder || '답변을 입력하세요...'}
            disabled={isAnswered || isSubmitting}
            className={cn(
              'w-full px-3 py-2 rounded-md border text-sm',
              'bg-white dark:bg-gray-800',
              'border-gray-300 dark:border-gray-600',
              'focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              (isAnswered || isSubmitting) && 'cursor-not-allowed opacity-60'
            )}
          />
          {!isAnswered && (
            <button
              onClick={handleSubmit}
              disabled={!localAnswer.trim() || isSubmitting}
              className={cn(
                'px-4 py-1.5 rounded-md text-sm font-medium transition-all',
                'bg-blue-500 text-white hover:bg-blue-600',
                'disabled:bg-gray-300 disabled:cursor-not-allowed'
              )}
            >
              {isSubmitting ? '제출 중...' : '확인'}
            </button>
          )}
        </div>
      )}

      {/* 제출 중 인디케이터 */}
      {isSubmitting && (
        <div className="mt-2 ml-9 flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          로드맵 구체화 중...
        </div>
      )}
    </div>
  );
}
