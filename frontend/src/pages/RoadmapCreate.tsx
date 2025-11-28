import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addMonths } from 'date-fns';
import { Map, BookOpen, Sparkles, Calendar, Clock, ArrowLeft, ArrowRight, MessageCircle, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { useStartInterview, useGenerateRoadmapWithContext } from '@/hooks';
import { InterviewQuestion, InterviewAnswer } from '@/lib/api';
import { cn } from '@/lib/utils';
import type { RoadmapMode } from '@/types';

type Step = 'mode' | 'topic' | 'duration' | 'interview' | 'generating';

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
    </div>
  );
}

function InterviewStep({
  questions,
  answers,
  onAnswerChange,
  isLoading,
}: {
  questions: InterviewQuestion[];
  answers: InterviewAnswer[];
  onAnswerChange: (questionId: string, answer: string) => void;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-primary-600 dark:text-primary-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI가 질문을 준비 중입니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          맞춤형 로드맵을 위한 질문을 생성하고 있어요...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400 rounded-full mb-4">
          <MessageCircle className="h-4 w-4" />
          <span className="text-sm font-medium">AI 인터뷰</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          몇 가지 질문에 답해주세요
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          더 맞춤화된 로드맵을 만들기 위해 필요한 정보입니다.
        </p>
      </div>

      <div className="space-y-6">
        {questions.map((question, index) => {
          const currentAnswer = answers.find((a) => a.question_id === question.id)?.answer || '';

          return (
            <div
              key={question.id}
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
                  value={currentAnswer}
                  onChange={(e) => onAnswerChange(question.id, e.target.value)}
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
                      onClick={() => onAnswerChange(question.id, option)}
                      className={cn(
                        'w-full text-left px-4 py-3 rounded-lg border transition-all',
                        currentAnswer === option
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
        })}
      </div>
    </div>
  );
}

function GeneratingState({ topic, hasContext }: { topic: string; hasContext: boolean }) {
  return (
    <div className="text-center py-12">
      <div className="relative inline-flex mb-6">
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="h-8 w-8 text-primary-600 dark:text-primary-400 animate-pulse" />
        </div>
        <svg className="h-24 w-24 animate-spin" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200 dark:text-dark-600"
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
            className="text-primary-600 dark:text-primary-400"
          />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {hasContext ? 'AI가 맞춤형 로드맵을 생성 중입니다' : 'AI가 로드맵을 생성 중입니다'}
      </h2>
      <p className="text-gray-500 dark:text-gray-400 mb-4">
        "{topic}"에 대한 {hasContext ? '개인 맞춤형' : ''} 학습 계획을 만들고 있어요.
      </p>
      <div className="text-sm text-gray-400 dark:text-gray-500">
        약 30초~1분 정도 소요됩니다.
      </div>
    </div>
  );
}

export function RoadmapCreate() {
  const navigate = useNavigate();
  const startInterview = useStartInterview();
  const generateWithContext = useGenerateRoadmapWithContext();

  const [step, setStep] = useState<Step>('mode');
  const [formData, setFormData] = useState<FormData>({
    mode: 'planning',
    topic: '',
    duration_months: 3,
    start_date: format(new Date(), 'yyyy-MM-dd'),
  });
  const [interviewQuestions, setInterviewQuestions] = useState<InterviewQuestion[]>([]);
  const [interviewAnswers, setInterviewAnswers] = useState<InterviewAnswer[]>([]);
  const [isLoadingInterview, setIsLoadingInterview] = useState(false);

  const canProceed = () => {
    switch (step) {
      case 'mode':
        return !!formData.mode;
      case 'topic':
        return formData.topic.length >= 2;
      case 'duration':
        return formData.duration_months > 0 && !!formData.start_date;
      case 'interview':
        // All questions must have answers
        return interviewQuestions.every((q) =>
          interviewAnswers.some((a) => a.question_id === q.id && a.answer.trim().length > 0)
        );
      default:
        return false;
    }
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setInterviewAnswers((prev) => {
      const existing = prev.findIndex((a) => a.question_id === questionId);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { question_id: questionId, answer };
        return updated;
      }
      return [...prev, { question_id: questionId, answer }];
    });
  };

  const handleNext = async () => {
    if (step === 'mode') {
      setStep('topic');
    } else if (step === 'topic') {
      setStep('duration');
    } else if (step === 'duration') {
      // Start interview
      setStep('interview');
      setIsLoadingInterview(true);
      try {
        const response = await startInterview.mutateAsync({
          topic: formData.topic,
          mode: formData.mode,
          duration_months: formData.duration_months,
        });
        setInterviewQuestions(response.data.questions);
        // Initialize answers
        setInterviewAnswers(response.data.questions.map((q) => ({ question_id: q.id, answer: '' })));
      } catch (error) {
        console.error('Failed to start interview:', error);
        // Fallback: skip interview and generate directly
        setStep('generating');
        try {
          const genResponse = await generateWithContext.mutateAsync({
            topic: formData.topic,
            duration_months: formData.duration_months,
            start_date: formData.start_date,
            mode: formData.mode,
            interview_answers: [],
            interview_questions: [],
          });
          navigate(`/roadmaps/${genResponse.data.roadmap_id}`);
        } catch (genError) {
          console.error('Failed to generate roadmap:', genError);
          setStep('duration');
        }
      } finally {
        setIsLoadingInterview(false);
      }
    } else if (step === 'interview') {
      // Generate roadmap with context
      setStep('generating');
      try {
        const response = await generateWithContext.mutateAsync({
          topic: formData.topic,
          duration_months: formData.duration_months,
          start_date: formData.start_date,
          mode: formData.mode,
          interview_answers: interviewAnswers,
          interview_questions: interviewQuestions,
        });
        navigate(`/roadmaps/${response.data.roadmap_id}`);
      } catch (error) {
        console.error('Failed to generate roadmap:', error);
        setStep('interview');
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
    }
  };

  const steps = ['mode', 'topic', 'duration', 'interview'];
  const currentStepIndex = steps.indexOf(step);
  const progressSteps = step === 'generating' ? steps : steps;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress */}
      {step !== 'generating' && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {progressSteps.map((s, i) => (
              <div
                key={s}
                className={`flex-1 h-1 rounded-full mx-1 ${
                  i <= currentStepIndex ? 'bg-primary-600 dark:bg-primary-500' : 'bg-gray-200 dark:bg-dark-600'
                }`}
              />
            ))}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
            단계 {currentStepIndex + 1} / {progressSteps.length}
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
          {step === 'interview' && (
            <InterviewStep
              questions={interviewQuestions}
              answers={interviewAnswers}
              onAnswerChange={handleAnswerChange}
              isLoading={isLoadingInterview}
            />
          )}
          {step === 'generating' && (
            <GeneratingState
              topic={formData.topic}
              hasContext={interviewAnswers.length > 0}
            />
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      {step !== 'generating' && !isLoadingInterview && (
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
            isLoading={startInterview.isPending || generateWithContext.isPending}
          >
            {step === 'interview' ? (
              <>
                <Sparkles className="h-4 w-4 mr-1" />
                맞춤형 로드맵 생성
              </>
            ) : step === 'duration' ? (
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
    </div>
  );
}
