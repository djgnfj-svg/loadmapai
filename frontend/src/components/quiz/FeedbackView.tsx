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
    if (isCorrect === true) return 'bg-green-50 border-green-200';
    if (isCorrect === false) return 'bg-red-50 border-red-200';
    if (score > 0) return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
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
          <span className="font-medium text-gray-900">
            문제 {questionIndex + 1}
          </span>
          <span className={cn(
            'px-2 py-0.5 text-xs rounded-full',
            isCorrect ? 'bg-green-100 text-green-700' :
            score > 0 ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          )}>
            {getStatusText()}
          </span>
        </div>
        <span className="text-sm text-gray-500">{question.points}점</span>
      </div>

      {/* Question */}
      <div className="mb-4">
        <p className="font-medium text-gray-900 mb-2">{question.question_text}</p>

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
                    isCorrectAnswer && 'bg-green-100 text-green-800',
                    isUserAnswer && !isCorrectAnswer && 'bg-red-100 text-red-800',
                    !isUserAnswer && !isCorrectAnswer && 'text-gray-600'
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
          <p className="text-sm text-gray-500 mb-1">내 답변:</p>
          <p className="p-3 bg-white rounded border text-sm">
            {getUserAnswerText()}
          </p>
        </div>
      )}

      {/* Correct Answer */}
      {question.correct_answer && question.question_type !== 'multiple_choice' && (
        <div className="mb-4">
          <p className="text-sm text-gray-500 mb-1">정답/모범답안:</p>
          <p className="p-3 bg-green-50 rounded border border-green-200 text-sm text-green-800">
            {question.correct_answer}
          </p>
        </div>
      )}

      {/* Feedback */}
      {userAnswer?.feedback && (
        <div className="mb-4">
          <p className="text-sm text-gray-500 mb-1">피드백:</p>
          <p className="p-3 bg-blue-50 rounded border border-blue-200 text-sm text-blue-800">
            {userAnswer.feedback}
          </p>
        </div>
      )}

      {/* Explanation */}
      {question.explanation && (
        <div>
          <p className="text-sm text-gray-500 mb-1">해설:</p>
          <p className="p-3 bg-gray-100 rounded text-sm text-gray-700">
            {question.explanation}
          </p>
        </div>
      )}
    </div>
  );
}
