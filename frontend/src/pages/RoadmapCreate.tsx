import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addMonths } from 'date-fns';
import { Map, BookOpen, Sparkles, Calendar, Clock, ArrowLeft, ArrowRight } from 'lucide-react';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { useGenerateRoadmap } from '@/hooks';
import type { RoadmapMode } from '@/types';

type Step = 'mode' | 'topic' | 'duration' | 'generating';

interface FormData {
  mode: RoadmapMode;
  topic: string;
  duration_months: number;
  start_date: string;
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
      description: '매일 해야 할 일을 체크하며 목표를 달성해 나가세요.',
      icon: Map,
      features: ['일별 태스크 체크리스트', '진행률 트래킹', '유연한 일정 관리'],
      color: 'primary',
    },
    {
      id: 'learning' as RoadmapMode,
      title: '러닝 모드',
      description: 'AI가 생성한 퀴즈로 학습 내용을 점검하세요.',
      icon: BookOpen,
      features: ['AI 퀴즈 자동 생성', '객관식/단답형/서술형', '피드백 및 복습'],
      color: 'green',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">학습 모드 선택</h2>
        <p className="text-gray-500">어떤 방식으로 학습을 진행하시겠어요?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((mode) => {
          const isSelected = selected === mode.id;
          const colorClasses = mode.color === 'primary'
            ? 'border-primary-500 bg-primary-50 ring-primary-500'
            : 'border-green-500 bg-green-50 ring-green-500';
          const iconColorClasses = mode.color === 'primary'
            ? 'bg-primary-100 text-primary-600'
            : 'bg-green-100 text-green-600';

          return (
            <button
              key={mode.id}
              onClick={() => onSelect(mode.id)}
              className={`text-left p-6 rounded-xl border-2 transition-all ${
                isSelected
                  ? `${colorClasses} ring-2`
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className={`inline-flex p-3 rounded-lg ${iconColorClasses} mb-4`}>
                <mode.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {mode.title}
              </h3>
              <p className="text-sm text-gray-500 mb-4">{mode.description}</p>
              <ul className="space-y-2">
                {mode.features.map((feature, i) => (
                  <li key={i} className="flex items-center text-sm text-gray-600">
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">학습 주제</h2>
        <p className="text-gray-500">어떤 것을 배우고 싶으신가요?</p>
      </div>

      <div>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="예: React 프론트엔드 개발 마스터하기"
          className="text-lg py-4"
        />
        <p className="mt-2 text-sm text-gray-500">
          구체적일수록 더 맞춤화된 로드맵이 생성됩니다.
        </p>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 mb-3">추천 주제</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onChange(suggestion)}
              className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                value === suggestion
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">학습 기간</h2>
        <p className="text-gray-500">얼마 동안 학습하시겠어요?</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {durations.map((d) => (
          <button
            key={d.months}
            onClick={() => onDurationChange(d.months)}
            className={`p-4 rounded-xl border-2 text-center transition-all ${
              duration === d.months
                ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-2xl font-bold text-gray-900">{d.months}</div>
            <div className="text-xs text-gray-500">개월</div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
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
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="inline h-4 w-4 mr-1" />
            종료 예정일
          </label>
          <div className="px-3 py-2 bg-gray-100 rounded-lg text-gray-700">
            {format(endDate, 'yyyy년 M월 d일')}
          </div>
        </div>
      </div>
    </div>
  );
}

function GeneratingState({ topic }: { topic: string }) {
  return (
    <div className="text-center py-12">
      <div className="relative inline-flex mb-6">
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="h-8 w-8 text-primary-600 animate-pulse" />
        </div>
        <svg className="h-24 w-24 animate-spin" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeDasharray="251.2"
            strokeDashoffset="188.4"
            strokeLinecap="round"
            className="text-primary-600"
          />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-gray-900 mb-2">
        AI가 로드맵을 생성 중입니다
      </h2>
      <p className="text-gray-500 mb-4">
        "{topic}"에 대한 맞춤형 학습 계획을 만들고 있어요.
      </p>
      <div className="text-sm text-gray-400">
        약 30초~1분 정도 소요됩니다.
      </div>
    </div>
  );
}

export function RoadmapCreate() {
  const navigate = useNavigate();
  const generateRoadmap = useGenerateRoadmap();

  const [step, setStep] = useState<Step>('mode');
  const [formData, setFormData] = useState<FormData>({
    mode: 'planning',
    topic: '',
    duration_months: 3,
    start_date: format(new Date(), 'yyyy-MM-dd'),
  });

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

  const handleNext = async () => {
    if (step === 'mode') {
      setStep('topic');
    } else if (step === 'topic') {
      setStep('duration');
    } else if (step === 'duration') {
      setStep('generating');
      try {
        const response = await generateRoadmap.mutateAsync({
          topic: formData.topic,
          duration_months: formData.duration_months,
          start_date: formData.start_date,
          mode: formData.mode,
        });
        navigate(`/roadmaps/${response.data.roadmap_id}`);
      } catch (error) {
        console.error('Failed to generate roadmap:', error);
        setStep('duration');
      }
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

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress */}
      {step !== 'generating' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {steps.map((s, i) => (
              <div
                key={s}
                className={`flex-1 h-1 rounded-full mx-1 ${
                  i <= currentStepIndex ? 'bg-primary-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <div className="text-sm text-gray-500 text-center">
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
              onDurationChange={(duration_months) =>
                setFormData({ ...formData, duration_months })
              }
              onStartDateChange={(start_date) =>
                setFormData({ ...formData, start_date })
              }
            />
          )}
          {step === 'generating' && <GeneratingState topic={formData.topic} />}
        </CardContent>
      </Card>

      {/* Navigation */}
      {step !== 'generating' && (
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
            isLoading={generateRoadmap.isPending}
          >
            {step === 'duration' ? (
              <>
                <Sparkles className="h-4 w-4 mr-1" />
                AI 로드맵 생성
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
    </div>
  );
}
