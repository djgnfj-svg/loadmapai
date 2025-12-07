import { cn } from '@/lib/utils';

interface MultipleChoiceQuestionProps {
  choices: string[];
  selectedAnswer: string;
  onSelect: (answer: string) => void;
  disabled?: boolean;
  correctAnswer?: string;
}

export function MultipleChoiceQuestion({
  choices,
  selectedAnswer,
  onSelect,
  disabled = false,
  correctAnswer,
}: MultipleChoiceQuestionProps) {
  const showResult = correctAnswer !== undefined;

  return (
    <div className="space-y-2">
      {choices.map((choice, index) => {
        const isSelected = selectedAnswer === String(index);
        const isCorrect = showResult && String(index) === correctAnswer;
        const isWrong = showResult && isSelected && !isCorrect;

        return (
          <button
            key={index}
            onClick={() => !disabled && onSelect(String(index))}
            disabled={disabled}
            className={cn(
              'w-full p-4 rounded-xl border-2 text-left transition-all',
              'flex items-center gap-3',
              !disabled && 'hover:border-primary-300 dark:hover:border-primary-600',
              isSelected && !showResult && 'border-primary-500 bg-primary-50 dark:bg-primary-900/20',
              !isSelected && !showResult && 'border-gray-200 dark:border-dark-600',
              isCorrect && 'border-green-500 bg-green-50 dark:bg-green-900/20',
              isWrong && 'border-red-500 bg-red-50 dark:bg-red-900/20',
              disabled && 'cursor-default'
            )}
          >
            <span
              className={cn(
                'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
                isSelected && !showResult && 'bg-primary-500 text-white',
                !isSelected && !showResult && 'bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400',
                isCorrect && 'bg-green-500 text-white',
                isWrong && 'bg-red-500 text-white',
                !isSelected && showResult && !isCorrect && 'bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400'
              )}
            >
              {String.fromCharCode(65 + index)}
            </span>
            <span
              className={cn(
                'flex-1',
                isCorrect && 'text-green-700 dark:text-green-300 font-medium',
                isWrong && 'text-red-700 dark:text-red-300'
              )}
            >
              {choice}
            </span>
            {isCorrect && (
              <svg
                className="w-5 h-5 text-green-600 dark:text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
            {isWrong && (
              <svg
                className="w-5 h-5 text-red-600 dark:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            )}
          </button>
        );
      })}
    </div>
  );
}
