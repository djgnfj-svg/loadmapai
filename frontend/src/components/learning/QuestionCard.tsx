import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';
import type { Question, QuestionType } from '@/types';
import { MultipleChoiceQuestion } from './MultipleChoiceQuestion';
import { EssayQuestion } from './EssayQuestion';
import { ShortAnswerQuestion } from './ShortAnswerQuestion';

interface QuestionCardProps {
  question: Question;
  questionNumber: number;
  totalQuestions: number;
  onAnswerChange: (answer: string) => void;
  onSubmit: (answer: string) => void;
  isSubmitting?: boolean;
  showResult?: boolean;
  correctAnswer?: string;
  explanation?: string;
}

export function QuestionCard({
  question,
  questionNumber,
  totalQuestions,
  onAnswerChange,
  onSubmit,
  isSubmitting = false,
  showResult = false,
  correctAnswer,
  explanation,
}: QuestionCardProps) {
  const [showHint, setShowHint] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState(
    question.user_answer?.answer_text || ''
  );

  const handleAnswerChange = (answer: string) => {
    setCurrentAnswer(answer);
    onAnswerChange(answer);
  };

  const getQuestionTypeLabel = (type: QuestionType) => {
    switch (type) {
      case 'ESSAY':
        return '서술형';
      case 'MULTIPLE_CHOICE':
        return '객관식';
      case 'SHORT_ANSWER':
        return '단답식';
    }
  };

  const getQuestionTypeColor = (type: QuestionType) => {
    switch (type) {
      case 'ESSAY':
        return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300';
      case 'MULTIPLE_CHOICE':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300';
      case 'SHORT_ANSWER':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
    }
  };

  const hasAnswer = currentAnswer.trim().length > 0;
  const isCorrect = question.user_answer?.is_correct;
  const feedback = question.user_answer?.feedback;

  return (
    <Card variant="elevated" className="relative">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Q{questionNumber} / {totalQuestions}
          </span>
          <span
            className={cn(
              'px-2 py-1 rounded-full text-xs font-medium',
              getQuestionTypeColor(question.question_type)
            )}
          >
            {getQuestionTypeLabel(question.question_type)}
          </span>
        </div>
        <CardTitle className="text-lg">{question.question_text}</CardTitle>
      </CardHeader>

      <CardContent>
        {/* Question Type Specific UI */}
        <div className="mb-4">
          {question.question_type === 'MULTIPLE_CHOICE' && (
            <MultipleChoiceQuestion
              choices={question.choices || []}
              selectedAnswer={currentAnswer}
              onSelect={handleAnswerChange}
              disabled={showResult}
              correctAnswer={showResult ? correctAnswer : undefined}
            />
          )}
          {question.question_type === 'ESSAY' && (
            <EssayQuestion
              value={currentAnswer}
              onChange={handleAnswerChange}
              disabled={showResult}
            />
          )}
          {question.question_type === 'SHORT_ANSWER' && (
            <ShortAnswerQuestion
              value={currentAnswer}
              onChange={handleAnswerChange}
              disabled={showResult}
            />
          )}
        </div>

        {/* Hint Button */}
        {question.hint && !showResult && (
          <div className="mb-4">
            <button
              onClick={() => setShowHint(!showHint)}
              className="flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              {showHint ? '힌트 숨기기' : '힌트 보기'}
            </button>
            {showHint && (
              <div className="mt-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  {question.hint}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Result Display */}
        {showResult && (
          <div className="mt-4 space-y-3">
            {/* Correct/Incorrect Badge */}
            <div
              className={cn(
                'flex items-center gap-2 p-3 rounded-lg',
                isCorrect
                  ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                  : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
              )}
            >
              {isCorrect ? (
                <>
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
                  <span className="font-medium text-green-700 dark:text-green-300">
                    정답입니다!
                  </span>
                </>
              ) : (
                <>
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
                  <span className="font-medium text-red-700 dark:text-red-300">
                    오답입니다
                  </span>
                </>
              )}
              {question.user_answer?.score !== null &&
                question.user_answer?.score !== undefined && (
                  <span className="ml-auto text-sm">
                    점수: {question.user_answer.score}점
                  </span>
                )}
            </div>

            {/* Correct Answer */}
            {!isCorrect && correctAnswer && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
                  정답:
                </p>
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  {correctAnswer}
                </p>
              </div>
            )}

            {/* Feedback */}
            {feedback && (
              <div className="p-3 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  피드백:
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {feedback}
                </p>
              </div>
            )}

            {/* Explanation */}
            {explanation && (
              <div className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                <p className="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">
                  해설:
                </p>
                <p className="text-sm text-purple-800 dark:text-purple-200">
                  {explanation}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        {!showResult && (
          <div className="mt-6 flex justify-end">
            <Button
              onClick={() => onSubmit(currentAnswer)}
              disabled={!hasAnswer || isSubmitting}
              isLoading={isSubmitting}
            >
              답변 저장
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
