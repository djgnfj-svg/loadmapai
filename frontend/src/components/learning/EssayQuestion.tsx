import { cn } from '@/lib/utils';

interface EssayQuestionProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  minLength?: number;
  maxLength?: number;
}

export function EssayQuestion({
  value,
  onChange,
  disabled = false,
  minLength = 50,
  maxLength = 2000,
}: EssayQuestionProps) {
  const characterCount = value.length;
  const isShort = characterCount < minLength && characterCount > 0;

  return (
    <div className="space-y-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="답변을 작성해주세요..."
        maxLength={maxLength}
        className={cn(
          'w-full min-h-[200px] p-4 rounded-xl border-2 resize-y',
          'text-gray-900 dark:text-white',
          'bg-white dark:bg-dark-800',
          'placeholder-gray-400 dark:placeholder-gray-500',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'disabled:bg-gray-50 dark:disabled:bg-dark-700 disabled:cursor-not-allowed',
          isShort
            ? 'border-yellow-400 dark:border-yellow-600'
            : 'border-gray-200 dark:border-dark-600'
        )}
      />
      <div className="flex justify-between items-center text-sm">
        <span
          className={cn(
            'text-gray-500 dark:text-gray-400',
            isShort && 'text-yellow-600 dark:text-yellow-400'
          )}
        >
          {isShort && `최소 ${minLength}자 이상 작성해주세요. `}
          {characterCount} / {maxLength}자
        </span>
        {!disabled && (
          <span className="text-gray-400 dark:text-gray-500">
            서술형 문제는 자세하게 작성할수록 좋습니다
          </span>
        )}
      </div>
    </div>
  );
}
