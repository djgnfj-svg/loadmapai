import { useState, useEffect } from 'react';
import { MessageCircle, Loader2, ChevronRight, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';
import type {
  InterviewQuestion,
  InterviewAnswer,
  InterviewQuestionsResponse,
  InterviewCompletedResponse,
} from '@/types';

interface DeepInterviewStepProps {
  sessionId: string | null;
  questionsData: InterviewQuestionsResponse | null;
  isLoading: boolean;
  error: string | null;
  onSubmitAnswers: (answers: InterviewAnswer[]) => void;
  isSubmitting: boolean;
}

export function DeepInterviewStep({
  sessionId,
  questionsData,
  isLoading,
  error,
  onSubmitAnswers,
  isSubmitting,
}: DeepInterviewStepProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  // Reset answers when questions change
  useEffect(() => {
    if (questionsData?.questions) {
      const initialAnswers: Record<string, string> = {};
      questionsData.questions.forEach((q) => {
        initialAnswers[q.id] = '';
      });
      setAnswers(initialAnswers);
    }
  }, [questionsData?.questions]);

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="relative inline-flex mb-4">
          <div className="p-4 rounded-full bg-primary-100 dark:bg-primary-500/20">
            <Sparkles className="h-8 w-8 text-primary-600 dark:text-primary-400 animate-pulse" />
          </div>
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI가 맞춤 질문을 생성 중입니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          주제에 최적화된 질문을 준비하고 있어요...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          오류가 발생했습니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">{error}</p>
      </div>
    );
  }

  if (!questionsData || !questionsData.questions.length) {
    return null;
  }

  const { questions } = questionsData;

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const allAnswered = questions.every(
    (q) => answers[q.id] && answers[q.id].trim().length > 0
  );

  const answeredCount = questions.filter(
    (q) => answers[q.id] && answers[q.id].trim().length > 0
  ).length;

  const handleSubmit = () => {
    const answersList: InterviewAnswer[] = Object.entries(answers)
      .filter(([_, value]) => value.trim().length > 0)
      .map(([question_id, answer]) => ({ question_id, answer }));
    onSubmitAnswers(answersList);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400 rounded-full mb-4">
          <MessageCircle className="h-4 w-4" />
          <span className="text-sm font-medium">
            AI 맞춤 질문 ({answeredCount}/{questions.length})
          </span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          로드맵을 위한 정보 수집
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          AI가 최적의 로드맵을 만들기 위해 필요한 정보입니다
        </p>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary-500 transition-all duration-300 ease-out"
          style={{ width: `${(answeredCount / questions.length) * 100}%` }}
        />
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {questions.map((question, index) => (
          <QuestionInput
            key={question.id}
            question={question}
            index={index}
            answer={answers[question.id] || ''}
            onAnswerChange={(answer) => handleAnswerChange(question.id, answer)}
          />
        ))}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end pt-4">
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={!allAnswered || isSubmitting}
          isLoading={isSubmitting}
          className="px-8"
        >
          {isSubmitting ? (
            '분석 중...'
          ) : (
            <>
              완료
              <CheckCircle2 className="h-4 w-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

interface QuestionInputProps {
  question: InterviewQuestion;
  index: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
}

function QuestionInput({ question, index, answer, onAnswerChange }: QuestionInputProps) {
  const isAnswered = answer.trim().length > 0;

  return (
    <div
      className={cn(
        'p-4 rounded-xl border transition-all duration-200',
        isAnswered
          ? 'border-primary-300 dark:border-primary-500/50 bg-primary-50/50 dark:bg-primary-500/5'
          : 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800'
      )}
    >
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        <span className={cn(
          'mr-2 inline-flex items-center justify-center w-6 h-6 rounded-full text-xs',
          isAnswered
            ? 'bg-primary-500 text-white'
            : 'bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400'
        )}>
          {isAnswered ? <CheckCircle2 className="h-3.5 w-3.5" /> : index + 1}
        </span>
        {question.question}
      </label>

      {question.question_type === 'text' ? (
        <textarea
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder={question.placeholder || '답변을 입력하세요...'}
          className={cn(
            'w-full px-4 py-3 rounded-lg border',
            'border-gray-200 dark:border-dark-600',
            'bg-gray-50 dark:bg-dark-700',
            'text-gray-900 dark:text-white',
            'placeholder-gray-400 dark:placeholder-gray-500',
            'focus:outline-none focus:ring-2 focus:ring-primary-500',
            'resize-none'
          )}
          rows={2}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {question.options?.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onAnswerChange(option)}
              className={cn(
                'text-left px-4 py-3 rounded-lg border transition-all text-sm',
                answer === option
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-400 font-medium'
                  : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500 text-gray-700 dark:text-gray-300'
              )}
            >
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Interview Completed View
interface InterviewCompletedProps {
  data: InterviewCompletedResponse;
  onGenerateRoadmap: () => void;
  isGenerating: boolean;
}

export function InterviewCompleted({ data, onGenerateRoadmap, isGenerating }: InterviewCompletedProps) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-500/20 rounded-full mb-4">
          <CheckCircle2 className="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          준비 완료!
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          AI가 분석한 핵심 정보를 확인하세요
        </p>
      </div>

      {/* Key Insights */}
      {data.key_insights && data.key_insights.length > 0 && (
        <div className="bg-gray-50 dark:bg-dark-700 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            핵심 인사이트
          </h3>
          <ul className="space-y-2">
            {data.key_insights.map((insight, i) => (
              <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-2 mr-2 flex-shrink-0" />
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Schedule Summary */}
      {data.schedule && (
        <div className="bg-gray-50 dark:bg-dark-700 rounded-xl p-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            학습 스케줄
          </h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {data.schedule.daily_minutes || 60}분
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">하루 학습</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {data.schedule.rest_days?.length || 0}일
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">주간 휴식</div>
            </div>
            <div>
              <div className="text-lg font-bold text-primary-600 dark:text-primary-400">
                {data.schedule.intensity === 'light' ? '여유롭게' :
                 data.schedule.intensity === 'intense' ? '빡세게' : '균형있게'}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">학습 강도</div>
            </div>
          </div>
        </div>
      )}

      {/* Generate Button */}
      <Button
        variant="primary"
        className="w-full"
        onClick={onGenerateRoadmap}
        isLoading={isGenerating}
        disabled={isGenerating}
      >
        {isGenerating ? '로드맵 생성 중...' : (
          <>
            <Sparkles className="h-4 w-4 mr-2" />
            맞춤형 로드맵 생성하기
          </>
        )}
      </Button>
    </div>
  );
}
