import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addMonths } from 'date-fns';
import { Map, BookOpen, Calendar, Clock, ArrowLeft, ArrowRight, Sparkles, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';
import type { RoadmapMode } from '@/types';

type Step = 'mode' | 'topic' | 'duration' | 'generating';

interface FormData {
  mode: RoadmapMode;
  topic: string;
  duration_months: number;
  start_date: string;
}

// Mode-specific text configuration
const MODE_PAGE_TEXT = {
  learning: {
    topicTitle: '학습 주제',
    topicSubtitle: '어떤 것을 배우고 싶으신가요?',
    topicPlaceholder: '예: React 프론트엔드 개발 마스터하기',
    topicHint: '구체적일수록 더 맞춤화된 학습 로드맵이 생성됩니다.',
    topicSuggestionsTitle: '추천 학습 주제',
    topicSuggestions: [
      'React 프론트엔드 개발',
      'Python 데이터 분석',
      '알고리즘 코딩 테스트',
      '영어 회화',
      'AWS 클라우드 자격증',
      '주식 투자 기초',
    ],
    durationTitle: '학습 기간',
    durationSubtitle: '얼마 동안 학습하시겠어요?',
  },
  planning: {
    topicTitle: '목표 설정',
    topicSubtitle: '어떤 목표를 달성하고 싶으신가요?',
    topicPlaceholder: '예: 3개월 안에 포트폴리오 웹사이트 완성하기',
    topicHint: '구체적일수록 더 맞춤화된 실행 계획이 생성됩니다.',
    topicSuggestionsTitle: '추천 목표',
    topicSuggestions: [
      '포트폴리오 웹사이트 제작',
      '정보처리기사 자격증 취득',
      '다이어트 10kg 감량',
      '토익 900점 달성',
      '사이드 프로젝트 런칭',
      '독서 50권 완독',
    ],
    durationTitle: '실행 기간',
    durationSubtitle: '얼마 동안 진행하시겠어요?',
  },
};

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
      description: '프로젝트, 자격증 준비, 운동 등 실천 위주의 목표에 적합합니다.',
      icon: Map,
      features: [
        '월별 → 주별 → 일별 세분화된 태스크',
        '체크리스트로 진행률 자동 계산',
        '프로젝트/자격증/운동 계획에 최적',
      ],
      color: 'primary',
      disabled: false,
    },
    {
      id: 'learning' as RoadmapMode,
      title: '러닝 모드',
      description: 'AI 퀴즈로 학습 이해도를 검증합니다. (준비 중)',
      icon: BookOpen,
      features: [
        '학습 주제별 AI 퀴즈 자동 생성',
        '객관식/단답형/서술형 문제 지원',
        '오답 해설 및 맞춤형 피드백 제공',
      ],
      color: 'green',
      disabled: true,
      badge: 'BETA',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">모드 선택</h2>
        <p className="text-gray-500 dark:text-gray-400">어떤 방식으로 진행하시겠어요?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((mode) => {
          const isSelected = selected === mode.id;
          const isDisabled = mode.disabled;
          const colorClasses = mode.color === 'primary'
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 ring-primary-500'
            : 'border-green-500 bg-green-50 dark:bg-green-500/10 ring-green-500';
          const iconColorClasses = mode.color === 'primary'
            ? 'bg-primary-100 dark:bg-primary-500/20 text-primary-600 dark:text-primary-400'
            : 'bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400';

          return (
            <button
              key={mode.id}
              onClick={() => !isDisabled && onSelect(mode.id)}
              disabled={isDisabled}
              className={cn(
                'text-left p-6 rounded-xl border-2 transition-all relative',
                isDisabled
                  ? 'opacity-60 cursor-not-allowed border-gray-200 dark:border-dark-600 bg-gray-50 dark:bg-dark-800'
                  : isSelected
                    ? `${colorClasses} ring-2`
                    : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
              )}
            >
              {mode.badge && (
                <span className="absolute top-3 right-3 px-2 py-0.5 text-xs font-bold rounded bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400">
                  {mode.badge}
                </span>
              )}
              <div className={cn(
                'inline-flex p-3 rounded-lg mb-4',
                isDisabled ? 'bg-gray-100 dark:bg-dark-600 text-gray-400 dark:text-gray-500' : iconColorClasses
              )}>
                <mode.icon className="h-6 w-6" />
              </div>
              <h3 className={cn(
                'text-lg font-semibold mb-2',
                isDisabled ? 'text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'
              )}>
                {mode.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{mode.description}</p>
              <ul className="space-y-2">
                {mode.features.map((feature, i) => (
                  <li key={i} className={cn(
                    'flex items-center text-sm',
                    isDisabled ? 'text-gray-400 dark:text-gray-500' : 'text-gray-600 dark:text-gray-300'
                  )}>
                    <span className={cn(
                      'w-1.5 h-1.5 rounded-full mr-2',
                      isDisabled
                        ? 'bg-gray-300 dark:bg-gray-600'
                        : mode.color === 'primary' ? 'bg-primary-500' : 'bg-green-500'
                    )} />
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
  mode,
}: {
  value: string;
  onChange: (value: string) => void;
  mode: RoadmapMode;
}) {
  const text = MODE_PAGE_TEXT[mode];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{text.topicTitle}</h2>
        <p className="text-gray-500 dark:text-gray-400">{text.topicSubtitle}</p>
      </div>

      <div>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={text.topicPlaceholder}
          className="text-lg py-4"
        />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {text.topicHint}
        </p>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">{text.topicSuggestionsTitle}</p>
        <div className="flex flex-wrap gap-2">
          {text.topicSuggestions.map((suggestion) => (
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
  mode,
}: {
  duration: number;
  startDate: string;
  onDurationChange: (duration: number) => void;
  onStartDateChange: (date: string) => void;
  mode: RoadmapMode;
}) {
  const text = MODE_PAGE_TEXT[mode];
  const durations = [
    { months: 1, label: '1개월', description: '집중 학습' },
    { months: 2, label: '2개월', description: '기초부터 차근차근' },
    { months: 3, label: '3개월', description: '균형 잡힌 학습' },
  ];

  const endDate = addMonths(new Date(startDate), duration);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{text.durationTitle}</h2>
        <p className="text-gray-500 dark:text-gray-400">{text.durationSubtitle}</p>
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
  const token = useAuthStore((state) => state.token);

  const [step, setStep] = useState<Step>('mode');
  const [formData, setFormData] = useState<FormData>({
    mode: 'planning',
    topic: '',
    duration_months: 3,
    start_date: format(new Date(), 'yyyy-MM-dd'),
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleGenerate = async () => {
    setStep('generating');
    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/roadmaps/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          topic: formData.topic,
          mode: formData.mode,
          duration_months: formData.duration_months,
          start_date: formData.start_date,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '로드맵 생성에 실패했습니다.');
      }

      const data = await response.json();
      navigate(`/roadmaps/${data.roadmap_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      setStep('duration');
      setIsGenerating(false);
    }
  };

  const handleNext = () => {
    if (step === 'mode') {
      setStep('topic');
    } else if (step === 'topic') {
      setStep('duration');
    } else if (step === 'duration') {
      handleGenerate();
    }
  };

  const handleBack = () => {
    if (step === 'topic') {
      setStep('mode');
    } else if (step === 'duration') {
      setStep('topic');
    }
  };

  const steps = ['mode', 'topic', 'duration'];
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
      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-xl">
          <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
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
              mode={formData.mode}
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
              mode={formData.mode}
            />
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
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
          disabled={!canProceed() || isGenerating}
        >
          {step === 'duration' ? (
            <>
              <Sparkles className="h-4 w-4 mr-1" />
              로드맵 생성
            </>
          ) : (
            <>
              다음
              <ArrowRight className="h-4 w-4 ml-1" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
