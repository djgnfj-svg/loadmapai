import { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';
import type { InterviewQuestion } from '../../types';
import type { AIFeedback, DraftRoadmap } from '../../hooks/useProgressiveRoadmap';

interface QuestionPanelProps {
  questions: InterviewQuestion[];
  answers: Map<string, string>;
  onAnswerChange: (questionId: string, answer: string) => void;
  onSubmit: (userWantsComplete?: boolean) => Promise<void>;  // 변경: 완료 여부 파라미터
  isSubmitting: boolean;
  className?: string;
  // 다중 라운드 인터뷰 props (NEW)
  currentRound?: number;
  maxRounds?: number;
  feedback?: AIFeedback | null;
  draftRoadmap?: DraftRoadmap | null;
  informationLevel?: 'insufficient' | 'minimal' | 'sufficient' | 'complete' | null;
  aiRecommendsComplete?: boolean;
  canComplete?: boolean;
}

export function QuestionPanel({
  questions,
  answers,
  onAnswerChange,
  onSubmit,
  isSubmitting,
  className,
  // 다중 라운드 인터뷰 props
  currentRound = 1,
  maxRounds = 10,
  feedback,
  draftRoadmap,
  informationLevel,
  aiRecommendsComplete = false,
  canComplete = false,
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

      {/* AI 피드백 (라운드 2 이상에서 표시) */}
      {feedback && currentRound > 1 && (
        <FeedbackCard feedback={feedback} informationLevel={informationLevel} />
      )}

      {/* 로드맵 초안 진행률 */}
      {draftRoadmap && draftRoadmap.completion_percentage > 0 && (
        <DraftProgressCard draftRoadmap={draftRoadmap} />
      )}

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
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        {/* AI 완료 추천 메시지 */}
        {aiRecommendsComplete && canComplete && (
          <div className="text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 p-2 rounded-lg text-center">
            AI가 충분한 정보가 모였다고 판단합니다. 완료해도 좋아요!
          </div>
        )}

        {/* 버튼 그룹 */}
        <div className={cn('flex gap-2', canComplete ? 'flex-row' : '')}>
          {/* 계속하기 버튼 */}
          <button
            onClick={() => onSubmit(false)}
            disabled={!allAnswered || isSubmitting}
            className={cn(
              'flex-1 py-3 px-4 rounded-lg font-semibold text-white transition-all',
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

          {/* 완료 버튼 (canComplete일 때만 표시) */}
          {canComplete && (
            <button
              onClick={() => onSubmit(true)}
              disabled={!allAnswered || isSubmitting}
              className={cn(
                'py-3 px-4 rounded-lg font-semibold transition-all',
                allAnswered && !isSubmitting
                  ? 'bg-green-500 hover:bg-green-400 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
              )}
            >
              이 정도면 됐어요
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// 피드백 카드 컴포넌트
function FeedbackCard({
  feedback,
  informationLevel,
}: {
  feedback: AIFeedback;
  informationLevel?: 'insufficient' | 'minimal' | 'sufficient' | 'complete' | null;
}) {
  const levelColors = {
    insufficient: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
    minimal: 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30',
    sufficient: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30',
    complete: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
  };

  const levelText = {
    insufficient: '정보 부족',
    minimal: '기본 정보',
    sufficient: '충분한 정보',
    complete: '완벽한 정보',
  };

  return (
    <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">AI 피드백</span>
        {informationLevel && (
          <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium', levelColors[informationLevel])}>
            {levelText[informationLevel]}
          </span>
        )}
      </div>

      {/* 솔직한 의견 */}
      {feedback.honest_opinion && (
        <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
          {feedback.honest_opinion}
        </p>
      )}

      {/* 격려 */}
      {feedback.encouragement && (
        <p className="text-sm text-green-600 dark:text-green-400 mb-2">
          {feedback.encouragement}
        </p>
      )}

      {/* 조언 */}
      {feedback.suggestions && feedback.suggestions.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">조언:</p>
          <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            {feedback.suggestions.map((suggestion, i) => (
              <li key={i} className="flex items-start gap-1">
                <span className="text-blue-500">-</span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// 로드맵 초안 진행률 카드
function DraftProgressCard({ draftRoadmap }: { draftRoadmap: DraftRoadmap }) {
  return (
    <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
          로드맵 초안
        </span>
        <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
          {draftRoadmap.completion_percentage}% 완성
        </span>
      </div>
      <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-500"
          style={{ width: `${draftRoadmap.completion_percentage}%` }}
        />
      </div>
      {draftRoadmap.months && draftRoadmap.months.length > 0 && (
        <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
          {draftRoadmap.months.slice(0, 2).map((m, i) => (
            <div key={i} className="truncate">
              {m.month}월: {m.title || '???'}
            </div>
          ))}
          {draftRoadmap.months.length > 2 && (
            <div>...외 {draftRoadmap.months.length - 2}개월</div>
          )}
        </div>
      )}
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
