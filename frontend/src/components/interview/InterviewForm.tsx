import { useState, useCallback, useEffect } from 'react';
import { MessageSquare, Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { QuestionCard } from './QuestionCard';
import type { InterviewQuestion, InterviewAnswer } from '@/types/interview';

interface InterviewFormProps {
  questions: InterviewQuestion[];
  round: number;
  maxRounds: number;
  onSubmit: (answers: InterviewAnswer[]) => void;
  isLoading: boolean;
}

export function InterviewForm({
  questions,
  round,
  maxRounds,
  onSubmit,
  isLoading,
}: InterviewFormProps) {
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset answers when round changes (new questions)
  useEffect(() => {
    setAnswers({});
    setErrors({});
  }, [round]);

  const handleAnswerChange = useCallback((questionId: string, value: string | string[]) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
    // Clear error when user starts typing
    if (errors[questionId]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  }, [errors]);

  const validateAnswers = useCallback(() => {
    const newErrors: Record<string, string> = {};

    questions.forEach((q) => {
      const answer = answers[q.id];
      if (!answer || (Array.isArray(answer) && answer.length === 0) || (typeof answer === 'string' && answer.trim() === '')) {
        newErrors[q.id] = '답변을 입력해주세요.';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [questions, answers]);

  const handleSubmit = useCallback(() => {
    if (!validateAnswers()) return;

    const formattedAnswers: InterviewAnswer[] = questions.map((q) => ({
      question_id: q.id,
      answer: answers[q.id] || '',
    }));

    onSubmit(formattedAnswers);
  }, [validateAnswers, questions, answers, onSubmit]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center p-3 rounded-full bg-primary-100 dark:bg-primary-500/20 mb-4">
          <MessageSquare className="h-6 w-6 text-primary-600 dark:text-primary-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {round === 1 ? '목표 설정 인터뷰' : '추가 질문'}
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          {round === 1
            ? '더 나은 학습 계획을 위해 몇 가지 질문에 답해주세요.'
            : '조금 더 구체적으로 알려주세요.'}
        </p>
        <div className="mt-2 text-sm text-gray-400 dark:text-gray-500">
          라운드 {round} / {maxRounds}
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {questions.map((question) => (
          <QuestionCard
            key={question.id}
            question={question}
            value={answers[question.id] || (question.type === 'multiselect' ? [] : '')}
            onChange={(value) => handleAnswerChange(question.id, value)}
            error={errors[question.id]}
          />
        ))}
      </div>

      {/* Submit button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isLoading}
          className="min-w-[120px]"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              분석 중...
            </>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              제출하기
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
