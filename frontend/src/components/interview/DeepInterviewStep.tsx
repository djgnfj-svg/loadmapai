import { useState, useEffect } from 'react';
import { MessageCircle, Loader2, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-react';
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

const STAGE_NAMES: Record<number, string> = {
  1: '목표 구체화',
  2: '현재 상태 파악',
  3: '제약 조건',
};

const STAGE_DESCRIPTIONS: Record<number, string> = {
  1: '어떤 목표를 이루고 싶으신가요?',
  2: '현재 어느 정도 알고 계신가요?',
  3: '학습 일정을 설정해볼까요?',
};

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
        <Loader2 className="h-12 w-12 animate-spin text-primary-600 dark:text-primary-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI가 질문을 준비 중입니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          맞춤형 로드맵을 위한 심층 질문을 생성하고 있어요...
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

  const { current_stage, stage_name, questions, is_followup } = questionsData;

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const allAnswered = questions.every(
    (q) => answers[q.id] && answers[q.id].trim().length > 0
  );

  const handleSubmit = () => {
    const answersList: InterviewAnswer[] = Object.entries(answers)
      .filter(([_, value]) => value.trim().length > 0)
      .map(([question_id, answer]) => ({ question_id, answer }));
    onSubmitAnswers(answersList);
  };

  return (
    <div className="space-y-6">
      {/* Stage Progress */}
      <div className="flex items-center justify-center gap-2 mb-6">
        {[1, 2, 3].map((stage) => (
          <div key={stage} className="flex items-center">
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors',
                stage < current_stage
                  ? 'bg-green-500 text-white'
                  : stage === current_stage
                  ? 'bg-primary-600 dark:bg-primary-500 text-white'
                  : 'bg-gray-200 dark:bg-dark-600 text-gray-500 dark:text-gray-400'
              )}
            >
              {stage < current_stage ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                stage
              )}
            </div>
            {stage < 3 && (
              <ChevronRight className="h-4 w-4 text-gray-400 dark:text-gray-500 mx-1" />
            )}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400 rounded-full mb-4">
          <MessageCircle className="h-4 w-4" />
          <span className="text-sm font-medium">
            {is_followup ? '추가 질문' : `Stage ${current_stage}: ${stage_name}`}
          </span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {is_followup ? '조금 더 구체적으로 알려주세요' : STAGE_DESCRIPTIONS[current_stage] || '질문에 답해주세요'}
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          {is_followup
            ? '더 정확한 로드맵을 위해 추가 정보가 필요해요.'
            : '더 맞춤화된 로드맵을 만들기 위해 필요한 정보입니다.'}
        </p>
      </div>

      {/* Questions */}
      <div className="space-y-6">
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
        >
          {current_stage < 3 ? (
            <>
              다음 단계로
              <ChevronRight className="h-4 w-4 ml-1" />
            </>
          ) : (
            <>
              인터뷰 완료
              <CheckCircle2 className="h-4 w-4 ml-1" />
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
  return (
    <div
      className={cn(
        'p-4 rounded-xl border',
        'border-gray-200 dark:border-dark-600',
        'bg-white dark:bg-dark-800'
      )}
    >
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        <span className="text-primary-600 dark:text-primary-400 mr-2">Q{index + 1}.</span>
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
          rows={3}
        />
      ) : (
        <div className="space-y-2">
          {question.options?.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onAnswerChange(option)}
              className={cn(
                'w-full text-left px-4 py-3 rounded-lg border transition-all',
                answer === option
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-400'
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
          인터뷰가 완료되었습니다!
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          AI가 분석한 핵심 인사이트를 확인하세요.
        </p>
      </div>

      {/* Key Insights */}
      {data.key_insights.length > 0 && (
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

      {/* Generate Button */}
      <Button
        variant="primary"
        className="w-full"
        onClick={onGenerateRoadmap}
        isLoading={isGenerating}
        disabled={isGenerating}
      >
        {isGenerating ? '로드맵 생성 중...' : '맞춤형 로드맵 생성하기'}
      </Button>
    </div>
  );
}
