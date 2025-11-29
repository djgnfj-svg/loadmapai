import { useState, useEffect, useCallback } from 'react';
import { MessageCircle, MapPin, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { SkeletonPreview } from '@/components/roadmap/SkeletonPreview';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type {
  InterviewQuestion,
  InterviewAnswer,
  InterviewQuestionsResponse,
  InterviewCompletedResponse,
  RoadmapMode,
  RoadmapSkeleton,
} from '@/types';

// Mode-specific text configuration
const MODE_TEXT = {
  learning: {
    title: '학습 계획 수립',
    subtitle: 'AI가 맞춤형 학습 계획을 설계합니다',
    questionPanelTitle: 'AI 맞춤 질문',
    previewPanelTitle: '로드맵 미리보기',
    generateButton: '로드맵 생성 시작',
    generatingButton: '세부 내용 생성 중...',
  },
  planning: {
    title: '실행 계획 수립',
    subtitle: 'AI가 맞춤형 실행 계획을 설계합니다',
    questionPanelTitle: 'AI 맞춤 질문',
    previewPanelTitle: '계획 미리보기',
    generateButton: '계획 생성 시작',
    generatingButton: '세부 내용 생성 중...',
  },
};

interface InterviewWithPreviewProps {
  topic: string;
  durationMonths: number;
  mode: RoadmapMode;
  questionsData: InterviewQuestionsResponse | null;
  isLoadingQuestions: boolean;
  questionError: string | null;
  onSubmitAnswers: (answers: InterviewAnswer[]) => void;
  isSubmitting: boolean;
  completedData: InterviewCompletedResponse | null;
  onGenerateRoadmap: () => void;
  isGenerating: boolean;
}

export function InterviewWithPreview({
  topic,
  durationMonths,
  mode,
  questionsData,
  isLoadingQuestions,
  questionError,
  onSubmitAnswers,
  isSubmitting,
  completedData,
  onGenerateRoadmap,
  isGenerating,
}: InterviewWithPreviewProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [skeleton, setSkeleton] = useState<RoadmapSkeleton | null>(null);
  const [skeletonLoading, setSkeletonLoading] = useState(false);
  const [skeletonError, setSkeletonError] = useState<string | null>(null);

  const text = MODE_TEXT[mode];

  // Fetch skeleton on mount
  useEffect(() => {
    const fetchSkeleton = async () => {
      setSkeletonLoading(true);
      setSkeletonError(null);
      try {
        const response = await api.post('/stream/roadmaps/skeleton', {
          topic,
          mode,
          duration_months: durationMonths,
        });
        if (response.data.success) {
          setSkeleton(response.data.skeleton);
        }
      } catch (err: any) {
        setSkeletonError(err.response?.data?.detail || '구조 생성 실패');
      } finally {
        setSkeletonLoading(false);
      }
    };

    fetchSkeleton();
  }, [topic, mode, durationMonths]);

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

  const handleAnswerChange = useCallback((questionId: string, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  }, []);

  const handleSubmit = useCallback(() => {
    const answersList: InterviewAnswer[] = Object.entries(answers)
      .filter(([_, value]) => value.trim().length > 0)
      .map(([question_id, answer]) => ({ question_id, answer }));
    onSubmitAnswers(answersList);
  }, [answers, onSubmitAnswers]);

  const questions = questionsData?.questions || [];
  const allAnswered = questions.every(
    (q) => answers[q.id] && answers[q.id].trim().length > 0
  );
  const answeredCount = questions.filter(
    (q) => answers[q.id] && answers[q.id].trim().length > 0
  ).length;

  // If completed, show generate button
  if (completedData) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
        {/* Left: Completion Summary */}
        <div className="flex flex-col">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200 dark:border-dark-600">
            <MessageCircle className="h-5 w-5 text-primary-500" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              인터뷰 완료
            </h3>
          </div>
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-500/20 rounded-full mb-4">
              <Sparkles className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              준비 완료!
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              인터뷰 결과를 바탕으로 세부 내용을 생성합니다
            </p>

            {/* Key Insights */}
            {completedData.key_insights && completedData.key_insights.length > 0 && (
              <div className="w-full bg-gray-50 dark:bg-dark-700 rounded-xl p-4 mb-6 text-left">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  핵심 인사이트
                </h4>
                <ul className="space-y-1">
                  {completedData.key_insights.slice(0, 3).map((insight, i) => (
                    <li key={i} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1.5 mr-2 flex-shrink-0" />
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <Button
              variant="primary"
              className="w-full max-w-sm"
              onClick={onGenerateRoadmap}
              isLoading={isGenerating}
              disabled={isGenerating}
            >
              {isGenerating ? text.generatingButton : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  {text.generateButton}
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right: Skeleton Preview */}
        <div className="flex flex-col bg-gray-50 dark:bg-dark-900/50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200 dark:border-dark-600">
            <MapPin className="h-5 w-5 text-primary-500" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {text.previewPanelTitle}
            </h3>
            {isGenerating && (
              <span className="ml-auto text-xs text-primary-500 flex items-center gap-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                세부 내용 채우는 중...
              </span>
            )}
          </div>
          <div className="flex-1 overflow-y-auto">
            <SkeletonPreview
              skeleton={skeleton}
              isLoading={skeletonLoading}
              error={skeletonError}
              topic={topic}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
      {/* Left: Question Panel */}
      <div className="flex flex-col">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200 dark:border-dark-600">
          <MessageCircle className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {text.questionPanelTitle}
          </h3>
          {questionsData && (
            <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
              {answeredCount}/{questions.length} 완료
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoadingQuestions ? (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-500 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">
                AI가 맞춤 질문을 생성 중입니다...
              </p>
            </div>
          ) : questionError ? (
            <div className="text-center py-12">
              <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 dark:text-red-400">{questionError}</p>
            </div>
          ) : questions.length > 0 ? (
            <div className="space-y-4">
              {/* Progress Bar */}
              <div className="w-full h-1.5 bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 transition-all duration-300 ease-out"
                  style={{ width: `${(answeredCount / questions.length) * 100}%` }}
                />
              </div>

              {/* Questions */}
              {questions.map((question, index) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  index={index}
                  answer={answers[question.id] || ''}
                  onAnswerChange={(answer) => handleAnswerChange(question.id, answer)}
                />
              ))}

              {/* Submit Button */}
              <div className="pt-4">
                <Button
                  variant="primary"
                  className="w-full"
                  onClick={handleSubmit}
                  disabled={!allAnswered || isSubmitting}
                  isLoading={isSubmitting}
                >
                  {isSubmitting ? '분석 중...' : '완료'}
                </Button>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Right: Skeleton Preview */}
      <div className="flex flex-col bg-gray-50 dark:bg-dark-900/50 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200 dark:border-dark-600">
          <MapPin className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {text.previewPanelTitle}
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto">
          <SkeletonPreview
            skeleton={skeleton}
            isLoading={skeletonLoading}
            error={skeletonError}
            topic={topic}
          />
        </div>
      </div>
    </div>
  );
}

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
}

function QuestionCard({ question, index, answer, onAnswerChange }: QuestionCardProps) {
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
        <span
          className={cn(
            'mr-2 inline-flex items-center justify-center w-5 h-5 rounded-full text-xs',
            isAnswered
              ? 'bg-primary-500 text-white'
              : 'bg-gray-200 dark:bg-dark-600 text-gray-600 dark:text-gray-400'
          )}
        >
          {index + 1}
        </span>
        {question.question}
      </label>

      {question.question_type === 'text' ? (
        <textarea
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder={question.placeholder || '답변을 입력하세요...'}
          className={cn(
            'w-full px-3 py-2 rounded-lg border text-sm',
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
        <div className="grid grid-cols-1 gap-2">
          {question.options?.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onAnswerChange(option)}
              className={cn(
                'text-left px-3 py-2 rounded-lg border transition-all text-sm',
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
