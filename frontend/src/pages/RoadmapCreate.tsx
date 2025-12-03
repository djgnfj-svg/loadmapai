import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addMonths } from 'date-fns';
import { Calendar, Clock, ArrowLeft, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { InterviewForm } from '@/components/interview';
import { useInterview } from '@/hooks/useInterview';
import { roadmapApi } from '@/lib/api';
import type { InterviewAnswer, InterviewContext } from '@/types/interview';

type Step = 'topic' | 'duration' | 'interview' | 'generating';

interface FormData {
  topic: string;
  duration_months: number;
  start_date: string;
  interview_context?: InterviewContext;
}

const TOPIC_SUGGESTIONS = [
  '포트폴리오 웹사이트 제작',
  '정보처리기사 자격증 취득',
  'React 프론트엔드 개발',
  '토익 900점 달성',
  'Python 데이터 분석',
  '사이드 프로젝트 런칭',
];

function TopicInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">목표 설정</h2>
        <p className="text-gray-500 dark:text-gray-400">어떤 목표를 달성하고 싶으신가요?</p>
      </div>

      <div>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="예: 3개월 안에 포트폴리오 웹사이트 완성하기"
          className="text-lg py-4"
        />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          구체적일수록 더 맞춤화된 실행 계획이 생성됩니다.
        </p>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">추천 목표</p>
        <div className="flex flex-wrap gap-2">
          {TOPIC_SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onChange(suggestion)}
              className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                value === suggestion
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400'
                  : 'border-gray-200 dark:border-dark-600 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-dark-500'
              }`}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function DurationSelection({
  duration,
  startDate,
  onDurationChange,
  onStartDateChange,
}: {
  duration: number;
  startDate: string;
  onDurationChange: (duration: number) => void;
  onStartDateChange: (date: string) => void;
}) {
  const durations = [
    { months: 1, label: '1개월' },
    { months: 2, label: '2개월' },
    { months: 3, label: '3개월' },
  ];

  const endDate = addMonths(new Date(startDate), duration);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">실행 기간</h2>
        <p className="text-gray-500 dark:text-gray-400">얼마 동안 진행하시겠어요?</p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {durations.map((d) => (
          <button
            key={d.months}
            onClick={() => onDurationChange(d.months)}
            className={`p-4 rounded-xl border-2 text-center transition-all ${
              duration === d.months
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 ring-2 ring-primary-500'
                : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
            }`}
          >
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{d.months}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">개월</div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <Calendar className="inline h-4 w-4 mr-1" />
            시작일
          </label>
          <Input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            min={format(new Date(), 'yyyy-MM-dd')}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <Clock className="inline h-4 w-4 mr-1" />
            종료 예정일
          </label>
          <div className="px-3 py-2 bg-gray-100 dark:bg-dark-700 rounded-lg text-gray-700 dark:text-gray-300">
            {format(endDate, 'yyyy년 M월 d일')}
          </div>
        </div>
      </div>
    </div>
  );
}

function GeneratingState({ topic }: { topic: string }) {
  return (
    <div className="py-12 space-y-6">
      <div className="text-center">
        <div className="relative inline-flex mb-6">
          <div className="p-4 rounded-full bg-primary-100 dark:bg-primary-500/20">
            <Sparkles className="h-10 w-10 text-primary-600 dark:text-primary-400" />
          </div>
          <div className="absolute -bottom-1 -right-1">
            <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
          </div>
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI가 맞춤형 로드맵을 생성 중입니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          "{topic}"에 대한 개인 맞춤형 계획을 만들고 있어요
        </p>
      </div>

      <div className="max-w-xs mx-auto">
        <div className="h-2 bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 rounded-full animate-pulse"
            style={{ width: '60%' }}
          />
        </div>
        <p className="text-center text-sm text-gray-400 dark:text-gray-500 mt-2">
          잠시만 기다려주세요...
        </p>
      </div>
    </div>
  );
}

export function RoadmapCreate() {
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>('topic');
  const [formData, setFormData] = useState<FormData>({
    topic: '',
    duration_months: 3,
    start_date: format(new Date(), 'yyyy-MM-dd'),
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const generationAttemptedRef = useRef(false);

  // Interview hook
  const interview = useInterview();

  // Handlers
  const handleGenerate = useCallback(async (interviewContext?: InterviewContext) => {
    setStep('generating');
    setIsGenerating(true);
    setError(null);

    try {
      const response = await roadmapApi.generate({
        topic: formData.topic,
        mode: 'PLANNING',
        duration_months: formData.duration_months,
        start_date: formData.start_date,
        interview_context: interviewContext as unknown as Record<string, unknown>,
      });

      navigate(`/roadmaps/${response.data.roadmap_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      setStep('interview');
      setIsGenerating(false);
    }
  }, [formData.topic, formData.duration_months, formData.start_date, navigate]);

  const canProceed = () => {
    switch (step) {
      case 'topic':
        return formData.topic.length >= 2;
      case 'duration':
        return formData.duration_months > 0 && !!formData.start_date;
      default:
        return false;
    }
  };

  // Effects
  // Start interview when entering interview step
  useEffect(() => {
    if (step === 'interview' && !interview.sessionId && !interview.isLoading) {
      interview.startInterview(formData.topic, formData.duration_months);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step, interview.sessionId, interview.isLoading, formData.topic, formData.duration_months]);

  // Move to generating when interview is complete
  useEffect(() => {
    if (interview.interviewContext && step === 'interview' && !isGenerating && !generationAttemptedRef.current) {
      generationAttemptedRef.current = true;
      setFormData((prev) => ({
        ...prev,
        interview_context: interview.interviewContext!,
      }));
      handleGenerate(interview.interviewContext);
    }
  }, [interview.interviewContext, step, isGenerating, handleGenerate]);

  const handleInterviewSubmit = async (answers: InterviewAnswer[]) => {
    await interview.submitAnswers(answers);
  };

  const handleNext = () => {
    if (step === 'topic') {
      setStep('duration');
    } else if (step === 'duration') {
      setStep('interview');
    }
  };

  const handleBack = () => {
    if (step === 'duration') {
      setStep('topic');
    } else if (step === 'interview') {
      interview.reset();
      generationAttemptedRef.current = false;
      setStep('duration');
    }
  };

  const steps = ['topic', 'duration', 'interview'];
  const currentStepIndex = steps.indexOf(step);
  const showProgress = step !== 'generating';

  // Generating step
  if (step === 'generating') {
    return (
      <div className="max-w-2xl mx-auto">
        <Card variant="bordered">
          <CardContent>
            <GeneratingState topic={formData.topic} />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress */}
      {showProgress && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {steps.map((s, i) => (
              <div
                key={s}
                className={`flex-1 h-1 rounded-full mx-1 ${
                  i <= currentStepIndex ? 'bg-primary-600 dark:bg-primary-500' : 'bg-gray-200 dark:bg-dark-600'
                }`}
              />
            ))}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
            단계 {currentStepIndex + 1} / {steps.length}
          </div>
        </div>
      )}

      {/* Error message */}
      {(error || interview.error) && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-xl">
          <p className="text-red-600 dark:text-red-400 text-sm">{error || interview.error}</p>
        </div>
      )}

      <Card variant="bordered">
        <CardContent>
          {step === 'topic' && (
            <TopicInput
              value={formData.topic}
              onChange={(topic) => setFormData({ ...formData, topic })}
            />
          )}
          {step === 'duration' && (
            <DurationSelection
              duration={formData.duration_months}
              startDate={formData.start_date}
              onDurationChange={(duration_months) =>
                setFormData({ ...formData, duration_months })
              }
              onStartDateChange={(start_date) =>
                setFormData({ ...formData, start_date })
              }
            />
          )}
          {step === 'interview' && interview.questions.length > 0 && (
            <InterviewForm
              questions={interview.questions}
              round={interview.round}
              maxRounds={interview.maxRounds}
              onSubmit={handleInterviewSubmit}
              isLoading={interview.isLoading}
            />
          )}
          {step === 'interview' && interview.questions.length === 0 && interview.isLoading && (
            <div className="py-12 text-center">
              <Loader2 className="h-8 w-8 text-primary-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">질문을 준비하고 있습니다...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      {step !== 'interview' && (
        <div className="flex justify-between mt-6">
          <Button
            variant="ghost"
            onClick={step === 'topic' ? () => navigate(-1) : handleBack}
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            {step === 'topic' ? '취소' : '이전'}
          </Button>
          <Button
            variant="primary"
            onClick={handleNext}
            disabled={!canProceed() || isGenerating}
          >
            다음
            <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}

      {step === 'interview' && interview.questions.length > 0 && (
        <div className="flex justify-start mt-6">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            이전
          </Button>
        </div>
      )}
    </div>
  );
}
