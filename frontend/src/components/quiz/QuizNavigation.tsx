import { cn } from '@/lib/utils';
import type { Question, SubmitAnswerRequest } from '@/types';

interface QuizNavigationProps {
  questions: Question[];
  answers: SubmitAnswerRequest[];
  currentIndex: number;
  onNavigate: (index: number) => void;
}

export function QuizNavigation({
  questions,
  answers,
  currentIndex,
  onNavigate,
}: QuizNavigationProps) {
  const isAnswered = (index: number) => {
    const answer = answers[index];
    if (!answer) return false;
    return !!(answer.answer_text || answer.selected_option);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">문제 목록</h3>
      <div className="grid grid-cols-5 gap-2">
        {questions.map((_, index) => (
          <button
            key={index}
            onClick={() => onNavigate(index)}
            className={cn(
              'w-10 h-10 rounded-lg text-sm font-medium transition-colors',
              currentIndex === index
                ? 'bg-primary-600 text-white'
                : isAnswered(index)
                  ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-500/30'
                  : 'bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-600'
            )}
          >
            {index + 1}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-primary-600" />
          <span>현재</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-100 dark:bg-green-500/20" />
          <span>답변 완료</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-gray-100 dark:bg-dark-700" />
          <span>미답변</span>
        </div>
      </div>
    </div>
  );
}
