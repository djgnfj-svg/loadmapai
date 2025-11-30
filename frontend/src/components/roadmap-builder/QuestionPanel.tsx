import { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';
import type { InterviewQuestion } from '../../types';

interface QuestionPanelProps {
  questions: InterviewQuestion[];
  answers: Map<string, string>;
  onAnswerChange: (questionId: string, answer: string) => void;
  onSubmit: (userWantsComplete?: boolean) => Promise<void>;
  isSubmitting: boolean;
  className?: string;
  // 2라운드 인터뷰 시스템
  currentRound?: number;
  maxRounds?: number;
}

export function QuestionPanel({
  questions,
  answers,
  onAnswerChange,
  onSubmit,
  isSubmitting,
  className,
  currentRound = 1,
  maxRounds = 2,
}: QuestionPanelProps) {
  const answeredCount = answers.size;
  const totalCount = questions.length;
  const progress = totalCount > 0 ? Math.round((answeredCount / totalCount) * 100) : 0;
  const allAnswered = answeredCount === totalCount && totalCount > 0;

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 헤더 */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            AI 인터뷰
          </h2>
          {/* 라운드 표시 */}
          <span className="text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">
            라운드 {currentRound} / {maxRounds}
          </span>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {currentRound === 1
            ? '맞춤형 로드맵을 위해 몇 가지 질문드릴게요'
            : '추가 질문에 답변해주시면 더 정확한 로드맵을 만들 수 있어요'}
        </p>

        {/* 진행률 바 */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          {answeredCount} / {totalCount} 질문 완료
        </p>
      </div>

      {/* 질문 목록 */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {questions.map((question, index) => (
          <QuestionCard
            key={question.id}
            question={question}
            index={index}
            answer={answers.get(question.id) || ''}
            onAnswerChange={(answer) => onAnswerChange(question.id, answer)}
            disabled={isSubmitting}
          />
        ))}
      </div>

      {/* 제출 버튼 영역 */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => onSubmit(false)}
          disabled={!allAnswered || isSubmitting}
          className={cn(
            'w-full py-3 px-4 rounded-lg font-semibold text-white transition-all',
            allAnswered && !isSubmitting
              ? 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 shadow-lg shadow-blue-500/25'
              : 'bg-gray-300 dark:bg-gray-700 cursor-not-allowed'
          )}
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              분석 중...
            </span>
          ) : allAnswered ? (
            '답변 제출'
          ) : (
            `${totalCount - answeredCount}개 질문 남음`
          )}
        </button>
      </div>
    </div>
  );
}

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
  disabled: boolean;
}

const CUSTOM_INPUT_KEY = '__custom__';

function QuestionCard({
  question,
  index,
  answer,
  onAnswerChange,
  disabled,
}: QuestionCardProps) {
  const [localAnswer, setLocalAnswer] = useState(answer);
  const [isCustomInput, setIsCustomInput] = useState(false);
  const [customText, setCustomText] = useState('');
  const isAnswered = answer.trim().length > 0;

  // 외부에서 answer가 변경되면 localAnswer도 업데이트
  useEffect(() => {
    setLocalAnswer(answer);
    // 기존 옵션에 없는 답변이면 직접 입력으로 간주
    if (question.question_type === 'single_choice' && question.options && answer) {
      const isExistingOption = question.options.includes(answer);
      if (!isExistingOption && answer.trim()) {
        setIsCustomInput(true);
        setCustomText(answer);
      }
    }
  }, [answer, question.options, question.question_type]);

  const handleOptionSelect = (option: string) => {
    if (disabled) return;
    if (option === CUSTOM_INPUT_KEY) {
      setIsCustomInput(true);
      // 직접 입력 선택 시 기존 답변 초기화하지 않음
    } else {
      setIsCustomInput(false);
      setCustomText('');
      setLocalAnswer(option);
      onAnswerChange(option);
    }
  };

  const handleCustomTextChange = (value: string) => {
    if (disabled) return;
    setCustomText(value);
  };

  const handleCustomTextBlur = () => {
    if (customText.trim()) {
      setLocalAnswer(customText);
      onAnswerChange(customText);
    }
  };

  const handleTextChange = (value: string) => {
    if (disabled) return;
    setLocalAnswer(value);
  };

  const handleTextBlur = () => {
    if (localAnswer.trim() && localAnswer !== answer) {
      onAnswerChange(localAnswer);
    }
  };

  // 현재 선택이 직접 입력인지 또는 기존 옵션인지 확인
  const isCustomSelected = isCustomInput || (
    question.options &&
    localAnswer.trim() &&
    !question.options.includes(localAnswer)
  );

  return (
    <div
      className={cn(
        'p-4 rounded-lg border transition-all duration-200',
        isAnswered
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
          {/* 기존 옵션들 */}
          {question.options.map((option) => (
            <button
              key={option}
              onClick={() => handleOptionSelect(option)}
              disabled={disabled}
              className={cn(
                'w-full text-left px-3 py-2 rounded-md text-sm transition-all',
                localAnswer === option && !isCustomSelected
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600',
                disabled && 'cursor-not-allowed opacity-60'
              )}
            >
              {option}
            </button>
          ))}

          {/* 직접 입력 옵션 */}
          <button
            onClick={() => handleOptionSelect(CUSTOM_INPUT_KEY)}
            disabled={disabled}
            className={cn(
              'w-full text-left px-3 py-2 rounded-md text-sm transition-all border-2 border-dashed',
              isCustomSelected
                ? 'bg-purple-500 text-white border-purple-500'
                : 'bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500 text-gray-600 dark:text-gray-400',
              disabled && 'cursor-not-allowed opacity-60'
            )}
          >
            ✏️ 직접 입력
          </button>

          {/* 직접 입력 텍스트 필드 */}
          {isCustomSelected && (
            <div className="mt-2">
              <input
                type="text"
                value={customText || (isCustomSelected && localAnswer ? localAnswer : '')}
                onChange={(e) => handleCustomTextChange(e.target.value)}
                onBlur={handleCustomTextBlur}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCustomTextBlur();
                  }
                }}
                placeholder="나만의 답변을 입력하세요..."
                disabled={disabled}
                autoFocus
                className={cn(
                  'w-full px-3 py-2 rounded-md border text-sm',
                  'bg-white dark:bg-gray-800',
                  'border-purple-300 dark:border-purple-600',
                  'focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                  disabled && 'cursor-not-allowed opacity-60'
                )}
              />
            </div>
          )}
        </div>
      ) : (
        <div className="ml-9">
          <input
            type="text"
            value={localAnswer}
            onChange={(e) => handleTextChange(e.target.value)}
            onBlur={handleTextBlur}
            placeholder={question.placeholder || '답변을 입력하세요...'}
            disabled={disabled}
            className={cn(
              'w-full px-3 py-2 rounded-md border text-sm',
              'bg-white dark:bg-gray-800',
              'border-gray-300 dark:border-gray-600',
              'focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              disabled && 'cursor-not-allowed opacity-60'
            )}
          />
        </div>
      )}
    </div>
  );
}
