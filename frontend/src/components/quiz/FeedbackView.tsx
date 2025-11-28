import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Question, UserAnswer } from '@/types';

interface FeedbackViewProps {
  question: Question;
  userAnswer?: UserAnswer;
  questionIndex: number;
}

export function FeedbackView({ question, userAnswer, questionIndex }: FeedbackViewProps) {
  const isCorrect = userAnswer?.is_correct;
  const score = userAnswer?.score || 0;

  const getStatusIcon = () => {
    if (isCorrect === true) {
      return <CheckCircle2 className="h-6 w-6 text-green-600" />;
    } else if (isCorrect === false) {
      return <XCircle className="h-6 w-6 text-red-600" />;
    } else if (score > 0) {
      return <AlertCircle className="h-6 w-6 text-yellow-600" />;
    }
    return <XCircle className="h-6 w-6 text-gray-400" />;
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
      const option = userAnswer?.selected_option;
      if (!option) return '응답 없음';
      const fullOption = question.options?.find(o => o.startsWith(option));
      return fullOption || option;
    }
    return userAnswer?.answer_text || '응답 없음';
  };

  return (
    <div className={cn('p-4 rounded-lg border', getStatusColor())}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className="font-medium text-gray-900 dark:text-white">
            문제 {questionIndex + 1}
          </span>
          <span className={cn(
            'px-2 py-0.5 text-xs rounded-full',
            isCorrect ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400' :
            score > 0 ? 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400' :
            'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
          )}>
            {getStatusText()}
          </span>
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400">{question.points}점</span>
      </div>

      {/* Question */}
      <div className="mb-4">
        <p className="font-medium text-gray-900 dark:text-white mb-2">{question.question_text}</p>

        {/* Options for multiple choice */}
        {question.question_type === 'multiple_choice' && question.options && (
          <div className="space-y-1 text-sm">
            {question.options.map((option, i) => {
              const optionLetter = option.charAt(0);
              const isUserAnswer = userAnswer?.selected_option === optionLetter;
              const isCorrectAnswer = question.correct_answer === optionLetter;

              return (
                <div
                  key={i}
                  className={cn(
                    'p-2 rounded',
                    isCorrectAnswer && 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-400',
                    isUserAnswer && !isCorrectAnswer && 'bg-red-100 dark:bg-red-500/20 text-red-800 dark:text-red-400',
                    !isUserAnswer && !isCorrectAnswer && 'text-gray-600 dark:text-gray-400'
                  )}
                >
                  {option}
                  {isCorrectAnswer && <span className="ml-2 text-xs">(정답)</span>}
                  {isUserAnswer && !isCorrectAnswer && <span className="ml-2 text-xs">(내 답변)</span>}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* User Answer (for non-multiple choice) */}
      {question.question_type !== 'multiple_choice' && (
        <div className="mb-4">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">내 답변:</p>
          <p className="p-3 bg-white dark:bg-dark-700 rounded border dark:border-dark-600 text-sm text-gray-900 dark:text-white">
            {getUserAnswerText()}
          </p>
        </div>
      )}

      {/* Correct Answer */}
      {question.correct_answer && question.question_type !== 'multiple_choice' && (
        <div className="mb-4">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">정답/모범답안:</p>
          <p className="p-3 bg-green-50 dark:bg-green-500/10 rounded border border-green-200 dark:border-green-500/30 text-sm text-green-800 dark:text-green-400">
            {question.correct_answer}
          </p>
        </div>
      )}

      {/* Feedback */}
      {userAnswer?.feedback && (
        <div className="mb-4">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">피드백:</p>
          <p className="p-3 bg-blue-50 dark:bg-blue-500/10 rounded border border-blue-200 dark:border-blue-500/30 text-sm text-blue-800 dark:text-blue-400">
            {userAnswer.feedback}
          </p>
        </div>
      )}

      {/* Explanation */}
      {question.explanation && (
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">해설:</p>
          <p className="p-3 bg-gray-100 dark:bg-dark-700 rounded text-sm text-gray-700 dark:text-gray-300">
            {question.explanation}
          </p>
        </div>
      )}
    </div>
  );
}
