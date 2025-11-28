import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Question, UserAnswer } from '@/types';

interface FeedbackViewProps {
  question: Question;
  userAnswer?: UserAnswer;
  questionIndex: number;
}

// Convert index to letter (0 -> A, 1 -> B, etc.)
const indexToLetter = (index: number): string => {
  return String.fromCharCode(65 + index);
};

export function FeedbackView({ question, userAnswer, questionIndex }: FeedbackViewProps) {
  const isCorrect = userAnswer?.is_correct;
  const score = userAnswer?.score || 0;

  const getStatusIcon = () => {
    if (isCorrect === true) {
      return <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />;
    } else if (isCorrect === false) {
      return <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />;
    } else if (score > 0) {
      return <AlertCircle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />;
    }
    return <XCircle className="h-6 w-6 text-gray-400 dark:text-gray-500" />;
  };

  const getStatusText = () => {
    if (isCorrect === true) return '정답';
    if (isCorrect === false && score === 0) return '오답';
    if (score > 0) return `부분 점수 (${score}점)`;
    return '미응답';
  };

  const getStatusColor = () => {
    if (isCorrect === true) return 'bg-green-50 dark:bg-green-500/10 border-green-200 dark:border-green-500/30';
    if (isCorrect === false) return 'bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30';
    if (score > 0) return 'bg-yellow-50 dark:bg-yellow-500/10 border-yellow-200 dark:border-yellow-500/30';
    return 'bg-gray-50 dark:bg-dark-700 border-gray-200 dark:border-dark-600';
  };

  const getUserAnswerText = () => {
    if (question.question_type === 'multiple_choice') {
      const selectedLetter = userAnswer?.selected_option;
      if (!selectedLetter) return '응답 없음';
      // Convert letter back to index and get the option
      const index = selectedLetter.charCodeAt(0) - 65;
      const option = question.options?.[index];
      return option ? `${selectedLetter}) ${option}` : selectedLetter;
    }
    return userAnswer?.answer_text || '응답 없음';
  };

  return (
    <div className={cn('p-5 rounded-xl border-2', getStatusColor())}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <span className="font-semibold text-gray-900 dark:text-white">
            문제 {questionIndex + 1}
          </span>
          <span className={cn(
            'px-2.5 py-1 text-xs font-medium rounded-full',
            isCorrect ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400' :
            score > 0 ? 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400' :
            'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
          )}>
            {getStatusText()}
          </span>
        </div>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{question.points}점</span>
      </div>

      {/* Question */}
      <div className="mb-4">
        <p className="font-medium text-gray-900 dark:text-white mb-3">{question.question_text}</p>

        {/* Options for multiple choice */}
        {question.question_type === 'multiple_choice' && question.options && (
          <div className="space-y-2">
            {question.options.map((option, index) => {
              const optionLetter = indexToLetter(index);
              const isUserAnswer = userAnswer?.selected_option === optionLetter;
              const isCorrectAnswer = question.correct_answer === optionLetter;

              return (
                <div
                  key={index}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border transition-colors',
                    isCorrectAnswer && 'bg-green-100 dark:bg-green-500/20 border-green-300 dark:border-green-500/50',
                    isUserAnswer && !isCorrectAnswer && 'bg-red-100 dark:bg-red-500/20 border-red-300 dark:border-red-500/50',
                    !isUserAnswer && !isCorrectAnswer && 'bg-white dark:bg-dark-800 border-gray-200 dark:border-dark-600'
                  )}
                >
                  {/* Option Letter Badge */}
                  <span className={cn(
                    'flex-shrink-0 w-7 h-7 rounded-md flex items-center justify-center text-xs font-bold',
                    isCorrectAnswer
                      ? 'bg-green-500 text-white'
                      : isUserAnswer && !isCorrectAnswer
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400'
                  )}>
                    {optionLetter}
                  </span>
                  {/* Option Text */}
                  <span className={cn(
                    'flex-1 text-sm',
                    isCorrectAnswer
                      ? 'text-green-800 dark:text-green-300 font-medium'
                      : isUserAnswer && !isCorrectAnswer
                        ? 'text-red-800 dark:text-red-300'
                        : 'text-gray-600 dark:text-gray-400'
                  )}>
                    {option}
                  </span>
                  {/* Status Label */}
                  {isCorrectAnswer && (
                    <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-green-500 text-white rounded">
                      정답
                    </span>
                  )}
                  {isUserAnswer && !isCorrectAnswer && (
                    <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-red-500 text-white rounded">
                      내 선택
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* User Answer (for non-multiple choice) */}
      {question.question_type !== 'multiple_choice' && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">내 답변:</p>
          <p className="p-3 bg-white dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-600 text-sm text-gray-900 dark:text-white">
            {getUserAnswerText()}
          </p>
        </div>
      )}

      {/* Correct Answer (for non-multiple choice) */}
      {question.correct_answer && question.question_type !== 'multiple_choice' && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">정답/모범답안:</p>
          <p className="p-3 bg-green-50 dark:bg-green-500/10 rounded-lg border border-green-200 dark:border-green-500/30 text-sm text-green-800 dark:text-green-300">
            {question.correct_answer}
          </p>
        </div>
      )}

      {/* Feedback */}
      {userAnswer?.feedback && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">피드백:</p>
          <p className="p-3 bg-blue-50 dark:bg-blue-500/10 rounded-lg border border-blue-200 dark:border-blue-500/30 text-sm text-blue-800 dark:text-blue-300">
            {userAnswer.feedback}
          </p>
        </div>
      )}

      {/* Explanation */}
      {question.explanation && (
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">해설:</p>
          <p className="p-3 bg-gray-100 dark:bg-dark-700 rounded-lg text-sm text-gray-700 dark:text-gray-300">
            {question.explanation}
          </p>
        </div>
      )}
    </div>
  );
}
