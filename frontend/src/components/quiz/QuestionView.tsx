import { cn } from '@/lib/utils';
import type { Question, SubmitAnswerRequest } from '@/types';

interface QuestionViewProps {
  question: Question;
  questionIndex: number;
  totalQuestions: number;
  answer: SubmitAnswerRequest;
  onAnswerChange: (answer: Partial<SubmitAnswerRequest>) => void;
  isSubmitted?: boolean;
}

// Convert index to letter (0 -> A, 1 -> B, etc.)
const indexToLetter = (index: number): string => {
  return String.fromCharCode(65 + index); // 65 is 'A'
};

export function QuestionView({
  question,
  questionIndex,
  totalQuestions,
  answer,
  onAnswerChange,
  isSubmitted,
}: QuestionViewProps) {
  const handleOptionSelect = (index: number) => {
    if (isSubmitted) return;
    const optionLetter = indexToLetter(index);
    onAnswerChange({ selected_option: optionLetter });
  };

  const handleTextChange = (text: string) => {
    if (isSubmitted) return;
    onAnswerChange({ answer_text: text });
  };

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
          문제 {questionIndex + 1} / {totalQuestions}
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {question.points}점
        </span>
      </div>

      {/* Question Text */}
      <div className="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
        <p className="text-lg font-medium text-gray-900 dark:text-white">
          {question.question_text}
        </p>
      </div>

      {/* Answer Input */}
      <div className="space-y-3">
        {question.question_type === 'multiple_choice' && question.options && (
          <div className="space-y-2">
            {question.options.map((option, index) => {
              const optionLetter = indexToLetter(index);
              const isSelected = answer.selected_option === optionLetter;

              return (
                <button
                  key={index}
                  onClick={() => handleOptionSelect(index)}
                  disabled={isSubmitted}
                  className={cn(
                    'w-full text-left p-4 rounded-xl border-2 transition-all duration-200',
                    'flex items-center gap-3',
                    isSelected
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/20 shadow-md'
                      : 'border-gray-200 dark:border-dark-600 hover:border-primary-300 dark:hover:border-primary-500/50 hover:bg-gray-50 dark:hover:bg-dark-700',
                    isSubmitted && 'cursor-not-allowed opacity-75'
                  )}
                >
                  {/* Option Letter Badge */}
                  <span className={cn(
                    'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold transition-colors',
                    isSelected
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400'
                  )}>
                    {optionLetter}
                  </span>
                  {/* Option Text */}
                  <span className={cn(
                    'flex-1 font-medium',
                    isSelected ? 'text-primary-700 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'
                  )}>
                    {option}
                  </span>
                  {/* Selection Indicator */}
                  {isSelected && (
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {question.question_type === 'short_answer' && (
          <div>
            <input
              type="text"
              value={answer.answer_text || ''}
              onChange={(e) => handleTextChange(e.target.value)}
              disabled={isSubmitted}
              placeholder="답을 입력하세요"
              className={cn(
                'w-full p-4 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500',
                isSubmitted && 'cursor-not-allowed opacity-75 bg-gray-50 dark:bg-dark-800'
              )}
            />
          </div>
        )}

        {question.question_type === 'essay' && (
          <div>
            <textarea
              value={answer.answer_text || ''}
              onChange={(e) => handleTextChange(e.target.value)}
              disabled={isSubmitted}
              placeholder="답안을 작성하세요"
              rows={6}
              className={cn(
                'w-full p-4 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-700 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 resize-none',
                isSubmitted && 'cursor-not-allowed opacity-75 bg-gray-50 dark:bg-dark-800'
              )}
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              {(answer.answer_text || '').length} / 1000자
            </p>
          </div>
        )}
      </div>

      {/* Question Type Badge */}
      <div className="flex items-center gap-2">
        <span className={cn(
          'px-3 py-1.5 text-xs font-medium rounded-full',
          question.question_type === 'multiple_choice' && 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
          question.question_type === 'short_answer' && 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400',
          question.question_type === 'essay' && 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400',
        )}>
          {question.question_type === 'multiple_choice' && '객관식'}
          {question.question_type === 'short_answer' && '단답형'}
          {question.question_type === 'essay' && '서술형'}
        </span>
      </div>
    </div>
  );
}
