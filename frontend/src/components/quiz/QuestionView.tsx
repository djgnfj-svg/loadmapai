import { cn } from '@/lib/utils';
import type { Question, SubmitAnswerRequest } from '@/types';

interface QuestionViewProps {
  question: Question;
  questionIndex: number;
  totalQuestions: number;
  answer: SubmitAnswerRequest;
  onAnswerChange: (answer: SubmitAnswerRequest) => void;
  isSubmitted?: boolean;
}

export function QuestionView({
  question,
  questionIndex,
  totalQuestions,
  answer,
  onAnswerChange,
  isSubmitted,
}: QuestionViewProps) {
  const handleOptionSelect = (option: string) => {
    if (isSubmitted) return;
    // Extract option letter (e.g., "A" from "A) 선택지")
    const optionLetter = option.charAt(0);
    onAnswerChange({ ...answer, selected_option: optionLetter });
  };

  const handleTextChange = (text: string) => {
    if (isSubmitted) return;
    onAnswerChange({ ...answer, answer_text: text });
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
              const optionLetter = option.charAt(0);
              const isSelected = answer.selected_option === optionLetter;

              return (
                <button
                  key={index}
                  onClick={() => handleOptionSelect(option)}
                  disabled={isSubmitted}
                  className={cn(
                    'w-full text-left p-4 rounded-lg border-2 transition-all',
                    isSelected
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/20'
                      : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500',
                    isSubmitted && 'cursor-not-allowed opacity-75'
                  )}
                >
                  <span className={cn(
                    'font-medium',
                    isSelected ? 'text-primary-700 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                  )}>
                    {option}
                  </span>
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
                'w-full p-4 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500',
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
                'w-full p-4 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500',
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
          'px-2 py-1 text-xs rounded-full',
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
