import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addMonths } from 'date-fns';
import { Map, BookOpen, Sparkles, Calendar, Clock, ArrowLeft, ArrowRight, MessageCircle, Globe } from 'lucide-react';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { DeepInterviewStep, InterviewCompleted } from '@/components/interview';
import { StreamingGeneratingState, ProgressiveRoadmapPreview } from '@/components/roadmap';
import {
  useStartDeepInterview,
  useSubmitInterviewAnswers,
  useInterviewQuestions,
} from '@/hooks';
import { useRoadmapStreaming } from '@/hooks/useStreaming';
import { cn } from '@/lib/utils';
import type { RoadmapMode, InterviewAnswer, InterviewCompletedResponse } from '@/types';

type Step = 'mode' | 'topic' | 'duration' | 'interview' | 'completed' | 'generating';

interface FormData {
  mode: RoadmapMode;
  topic: string;
  duration_months: number;
  start_date: string;
  use_web_search: boolean;
}

function ModeSelection({
  selected,
  onSelect,
}: {
  selected: RoadmapMode | null;
  onSelect: (mode: RoadmapMode) => void;
}) {
  const modes = [
    {
      id: 'planning' as RoadmapMode,
      title: '플래닝 모드',
      description: '프로젝트, 자격증 준비, 운동 등 실천 위주의 목표에 적합합니다. 매일 해야 할 일을 체크하며 꾸준히 목표를 달성해 나가세요.',
      icon: Map,
      features: [
        '월별 → 주별 → 일별 세분화된 태스크',
        '체크리스트로 진행률 자동 계산',
        '프로젝트/자격증/운동 계획에 최적',
      ],
      color: 'primary',
    },
    {
      id: 'learning' as RoadmapMode,
      title: '러닝 모드',
      description: '새로운 지식을 학습하고 이해도를 검증하고 싶을 때 적합합니다. AI가 학습 내용을 기반으로 퀴즈를 생성하고 피드백을 제공합니다.',
      icon: BookOpen,
      features: [
        '학습 주제별 AI 퀴즈 자동 생성',
        '객관식/단답형/서술형 문제 지원',
        '오답 해설 및 맞춤형 피드백 제공',
      ],
      color: 'green',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">학습 모드 선택</h2>
        <p className="text-gray-500 dark:text-gray-400">어떤 방식으로 학습을 진행하시겠어요?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((mode) => {
          const isSelected = selected === mode.id;
          const colorClasses = mode.color === 'primary'
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 ring-primary-500'
            : 'border-green-500 bg-green-50 dark:bg-green-500/10 ring-green-500';
          const iconColorClasses = mode.color === 'primary'
            ? 'bg-primary-100 dark:bg-primary-500/20 text-primary-600 dark:text-primary-400'
            : 'bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400';

          return (
            <button
              key={mode.id}
              onClick={() => onSelect(mode.id)}
              className={`text-left p-6 rounded-xl border-2 transition-all ${
                isSelected
                  ? `${colorClasses} ring-2`
                  : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
              }`}
            >
              <div className={`inline-flex p-3 rounded-lg ${iconColorClasses} mb-4`}>
                <mode.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {mode.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{mode.description}</p>
              <ul className="space-y-2">
                {mode.features.map((feature, i) => (
                  <li key={i} className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <span className={`w-1.5 h-1.5 rounded-full mr-2 ${
                      mode.color === 'primary' ? 'bg-primary-500' : 'bg-green-500'
                    }`} />
                    {feature}
                  </li>
                ))}
              </ul>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function TopicInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  const suggestions = [
    'React 프론트엔드 개발',
    'Python 데이터 분석',
    '알고리즘 코딩 테스트',
    '영어 회화',
    'AWS 클라우드 자격증',
    '주식 투자 기초',
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">학습 주제</h2>
        <p className="text-gray-500 dark:text-gray-400">어떤 것을 배우고 싶으신가요?</p>
      </div>

      <div>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="예: React 프론트엔드 개발 마스터하기"
          className="text-lg py-4"
        />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          구체적일수록 더 맞춤화된 로드맵이 생성됩니다.
        </p>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">추천 주제</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion) => (
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
  useWebSearch,
  onDurationChange,
  onStartDateChange,
  onWebSearchChange,
}: {
  duration: number;
  startDate: string;
  useWebSearch: boolean;
  onDurationChange: (duration: number) => void;
  onStartDateChange: (date: string) => void;
  onWebSearchChange: (enabled: boolean) => void;
}) {
  const durations = [
    { months: 1, label: '1개월', description: '집중 학습' },
    { months: 2, label: '2개월', description: '기초부터 차근차근' },
    { months: 3, label: '3개월', description: '균형 잡힌 학습' },
    { months: 4, label: '4개월', description: '깊이 있는 학습' },
    { months: 6, label: '6개월', description: '전문가 과정' },
  ];

  const endDate = addMonths(new Date(startDate), duration);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">학습 기간</h2>
        <p className="text-gray-500 dark:text-gray-400">얼마 동안 학습하시겠어요?</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
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

      {/* Web Search Option */}
      <div className="border-t border-gray-200 dark:border-dark-600 pt-4">
        <button
          type="button"
          onClick={() => onWebSearchChange(!useWebSearch)}
          className={cn(
            'w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all',
            useWebSearch
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/10'
              : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
          )}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-2 rounded-lg',
              useWebSearch
                ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400'
                : 'bg-gray-100 dark:bg-dark-600 text-gray-500 dark:text-gray-400'
            )}>
              <Globe className="h-5 w-5" />
            </div>
            <div className="text-left">
              <div className={cn(
                'font-medium',
                useWebSearch ? 'text-blue-700 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'
              )}>
                실시간 웹 검색
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                최신 강의, 자료, 학습 경로를 검색하여 반영합니다
              </div>
            </div>
          </div>
          <div className={cn(
            'w-11 h-6 rounded-full transition-colors relative',
            useWebSearch ? 'bg-blue-500' : 'bg-gray-300 dark:bg-dark-500'
          )}>
            <div className={cn(
              'absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow',
              useWebSearch ? 'translate-x-5' : 'translate-x-0.5'
            )} />
          </div>
        </button>
      </div>
    </div>
  );
}

export function RoadmapCreate() {
  const navigate = useNavigate();
  const startInterview = useStartDeepInterview();

  // Streaming hook for roadmap generation
  const roadmapStreaming = useRoadmapStreaming();

  const [step, setStep] = useState<Step>('mode');
  const [formData, setFormData] = useState<FormData>({
    mode: 'planning',
    topic: '',
    duration_months: 3,
    start_date: format(new Date(), 'yyyy-MM-dd'),
    use_web_search: true,
  });
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [completedData, setCompletedData] = useState<InterviewCompletedResponse | null>(null);
  const [interviewError, setInterviewError] = useState<string | null>(null);

  // Fetch questions for current session
  const {
    data: questionsData,
    isLoading: isLoadingQuestions,
    refetch: refetchQuestions,
  } = useInterviewQuestions(sessionId || '');

  // Submit answers mutation
  const submitAnswers = useSubmitInterviewAnswers(sessionId || '');

  // Handle questions response - check if interview is complete
  useEffect(() => {
    if (questionsData) {
      if (questionsData.is_complete) {
        // Interview completed - fetch completed data
        setCompletedData({
          session_id: questionsData.session_id,
          is_complete: true,
          compiled_context: '',
          key_insights: [],
          schedule: {},
          can_generate_roadmap: true,
        });
        setStep('completed');
      }
    }
  }, [questionsData]);

  // Handle streaming completion
  useEffect(() => {
    if (roadmapStreaming.result && !roadmapStreaming.isStreaming) {
      const result = roadmapStreaming.result as { roadmap_id: string };
      if (result.roadmap_id) {
        navigate(`/roadmaps/${result.roadmap_id}`);
      }
    }
  }, [roadmapStreaming.result, roadmapStreaming.isStreaming, navigate]);

  // Handle streaming error
  useEffect(() => {
    if (roadmapStreaming.error && !roadmapStreaming.isStreaming) {
      setStep('completed');
    }
  }, [roadmapStreaming.error, roadmapStreaming.isStreaming]);

  const canProceed = () => {
    switch (step) {
      case 'mode':
        return !!formData.mode;
      case 'topic':
        return formData.topic.length >= 2;
      case 'duration':
        return formData.duration_months > 0 && !!formData.start_date;
      default:
        return false;
    }
  };

  const handleAnswersSubmit = async (answers: InterviewAnswer[]) => {
    if (!sessionId) return;

    try {
      setInterviewError(null);
      const response = await submitAnswers.mutateAsync(answers);

      // Check if interview is complete
      if (response.data.is_complete) {
        setCompletedData(response.data as InterviewCompletedResponse);
        setStep('completed');
      } else {
        // Refetch questions for next stage
        await refetchQuestions();
      }
    } catch (error) {
      console.error('Failed to submit answers:', error);
      setInterviewError('답변 제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!sessionId) return;

    setStep('generating');
    roadmapStreaming.reset();

    // Use streaming to generate roadmap
    await roadmapStreaming.generateRoadmap({
      interview_session_id: sessionId,
      start_date: formData.start_date,
      use_web_search: formData.use_web_search,
    });
  };

  const handleNext = async () => {
    if (step === 'mode') {
      setStep('topic');
    } else if (step === 'topic') {
      setStep('duration');
    } else if (step === 'duration') {
      // Start deep interview
      setStep('interview');
      try {
        setInterviewError(null);
        const response = await startInterview.mutateAsync({
          topic: formData.topic,
          mode: formData.mode,
          duration_months: formData.duration_months,
        });
        setSessionId(response.data.session_id);
      } catch (error) {
        console.error('Failed to start interview:', error);
        setInterviewError('인터뷰 시작 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    }
  };

  const handleBack = () => {
    if (step === 'topic') {
      setStep('mode');
    } else if (step === 'duration') {
      setStep('topic');
    } else if (step === 'interview') {
      setStep('duration');
      setSessionId(null);
      setInterviewError(null);
    } else if (step === 'completed') {
      setStep('interview');
    }
  };

  const steps = ['mode', 'topic', 'duration', 'interview'];
  const currentStepIndex = steps.indexOf(step);
  const showProgress = step !== 'generating' && step !== 'completed';

  // Generating step has different layout (full width with split view)
  if (step === 'generating') {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Progress Panel */}
          <Card variant="bordered">
            <CardContent>
              <StreamingGeneratingState
                topic={formData.topic}
                events={roadmapStreaming.events}
                currentEvent={roadmapStreaming.currentEvent}
                progress={roadmapStreaming.progress}
                isStreaming={roadmapStreaming.isStreaming}
                error={roadmapStreaming.error}
              />
            </CardContent>
          </Card>

          {/* Right: Progressive Roadmap Preview */}
          <Card variant="bordered">
            <CardContent>
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Map className="h-5 w-5 text-primary-500" />
                  로드맵 미리보기
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  생성되는 로드맵을 실시간으로 확인하세요
                </p>
              </div>
              <div className="max-h-[500px] overflow-y-auto custom-scrollbar">
                <ProgressiveRoadmapPreview
                  partialRoadmap={roadmapStreaming.partialRoadmap}
                  isStreaming={roadmapStreaming.isStreaming}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Cancel button */}
        {roadmapStreaming.isStreaming && (
          <div className="flex justify-center mt-6">
            <Button
              variant="ghost"
              onClick={() => {
                roadmapStreaming.abort();
                setStep('completed');
              }}
            >
              취소
            </Button>
          </div>
        )}
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

      <Card variant="bordered">
        <CardContent>
          {step === 'mode' && (
            <ModeSelection
              selected={formData.mode}
              onSelect={(mode) => setFormData({ ...formData, mode })}
            />
          )}
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
              useWebSearch={formData.use_web_search}
              onDurationChange={(duration_months) =>
                setFormData({ ...formData, duration_months })
              }
              onStartDateChange={(start_date) =>
                setFormData({ ...formData, start_date })
              }
              onWebSearchChange={(use_web_search) =>
                setFormData({ ...formData, use_web_search })
              }
            />
          )}
          {step === 'interview' && (
            <DeepInterviewStep
              sessionId={sessionId}
              questionsData={questionsData || null}
              isLoading={startInterview.isPending || isLoadingQuestions}
              error={interviewError}
              onSubmitAnswers={handleAnswersSubmit}
              isSubmitting={submitAnswers.isPending}
            />
          )}
          {step === 'completed' && completedData && (
            <InterviewCompleted
              data={completedData}
              onGenerateRoadmap={handleGenerateRoadmap}
              isGenerating={false}
            />
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      {step !== 'generating' && step !== 'interview' && step !== 'completed' && (
        <div className="flex justify-between mt-6">
          <Button
            variant="ghost"
            onClick={step === 'mode' ? () => navigate(-1) : handleBack}
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            {step === 'mode' ? '취소' : '이전'}
          </Button>
          <Button
            variant="primary"
            onClick={handleNext}
            disabled={!canProceed()}
            isLoading={startInterview.isPending}
          >
            {step === 'duration' ? (
              <>
                <MessageCircle className="h-4 w-4 mr-1" />
                다음 (AI 인터뷰)
              </>
            ) : (
              <>
                다음
                <ArrowRight className="h-4 w-4 ml-1" />
              </>
            )}
          </Button>
        </div>
      )}

      {/* Back button for interview step */}
      {step === 'interview' && !startInterview.isPending && !isLoadingQuestions && (
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
