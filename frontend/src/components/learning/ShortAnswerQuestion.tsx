import { cn } from '@/lib/utils';

interface ShortAnswerQuestionProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ShortAnswerQuestion({
  value,
  onChange,
  disabled = false,
  placeholder = '정답을 입력하세요...',
}: ShortAnswerQuestionProps) {
  return (
    <div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        className={cn(
          'w-full p-4 rounded-xl border-2',
          'text-gray-900 dark:text-white text-lg',
          'bg-white dark:bg-dark-800',
          'placeholder-gray-400 dark:placeholder-gray-500',
          'border-gray-200 dark:border-dark-600',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
          'disabled:bg-gray-50 dark:disabled:bg-dark-700 disabled:cursor-not-allowed'
        )}
      />
      {!disabled && (
        <p className="mt-2 text-sm text-gray-400 dark:text-gray-500">
          단답식 문제입니다. 핵심 용어나 답을 간결하게 작성하세요.
        </p>
      )}
    </div>
  );
}
