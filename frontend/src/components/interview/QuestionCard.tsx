import { InterviewQuestion, CATEGORY_META } from '@/types/interview';

interface QuestionCardProps {
  question: InterviewQuestion;
  value: string | string[];
  onChange: (value: string | string[]) => void;
  error?: string;
}

export function QuestionCard({ question, value, onChange, error }: QuestionCardProps) {
  const meta = CATEGORY_META[question.category];

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const handleSelectChange = (option: string) => {
    onChange(option);
  };

  const handleMultiSelectChange = (option: string) => {
    const currentValues = Array.isArray(value) ? value : [];
    if (currentValues.includes(option)) {
      onChange(currentValues.filter((v) => v !== option));
    } else {
      onChange([...currentValues, option]);
    }
  };

  return (
    <div className="p-4 border border-gray-200 dark:border-dark-600 rounded-xl">
      {/* Category badge */}
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${meta.bgColor} ${meta.color}`}>
          {meta.label}
        </span>
      </div>

      {/* Question */}
      <p className="text-gray-900 dark:text-white font-medium mb-4">{question.question}</p>

      {/* Answer input */}
      {question.type === 'text' && (
        <textarea
          value={typeof value === 'string' ? value : ''}
          onChange={handleTextChange}
          placeholder="답변을 입력해주세요..."
          rows={3}
          className={`w-full px-3 py-2 rounded-lg border ${
            error
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 dark:border-dark-500 focus:ring-primary-500'
          } focus:outline-none focus:ring-2 bg-white dark:bg-dark-700 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 resize-none`}
        />
      )}

      {question.type === 'select' && question.options && (
        <div className="space-y-2">
          {question.options.map((option) => (
            <label
              key={option}
              className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                value === option
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
                  : 'border-gray-200 dark:border-dark-600 hover:bg-gray-50 dark:hover:bg-dark-700'
              }`}
            >
              <input
                type="radio"
                name={question.id}
                checked={value === option}
                onChange={() => handleSelectChange(option)}
                className="w-4 h-4 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-gray-700 dark:text-gray-300">{option}</span>
            </label>
          ))}
        </div>
      )}

      {question.type === 'multiselect' && question.options && (
        <div className="space-y-2">
          {question.options.map((option) => {
            const isChecked = Array.isArray(value) && value.includes(option);
            return (
              <label
                key={option}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  isChecked
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
                    : 'border-gray-200 dark:border-dark-600 hover:bg-gray-50 dark:hover:bg-dark-700'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => handleMultiSelectChange(option)}
                  className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
                <span className="text-gray-700 dark:text-gray-300">{option}</span>
              </label>
            );
          })}
        </div>
      )}

      {/* Error message */}
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  );
}
