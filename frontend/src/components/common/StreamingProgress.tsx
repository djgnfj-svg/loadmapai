import { useState, useEffect, useMemo } from 'react';
import {
  Loader2,
  Search,
  Brain,
  Target,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  MessageSquare,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StreamEvent, StreamEventType } from '@/hooks/useStreaming';

interface StreamingProgressProps {
  events: StreamEvent[];
  currentEvent: StreamEvent | null;
  progress: number;
  isStreaming: boolean;
  error: string | null;
  className?: string;
}

const EVENT_CONFIG: Record<
  StreamEventType,
  { icon: typeof Loader2; label: string; color: string }
> = {
  start: { icon: Sparkles, label: '시작', color: 'text-primary-500' },
  progress: { icon: Loader2, label: '진행 중', color: 'text-primary-500' },
  complete: { icon: CheckCircle2, label: '완료', color: 'text-green-500' },
  error: { icon: AlertCircle, label: '오류', color: 'text-red-500' },
  generating_questions: {
    icon: MessageSquare,
    label: '질문 생성',
    color: 'text-blue-500',
  },
  evaluating_answers: {
    icon: Brain,
    label: '답변 분석',
    color: 'text-purple-500',
  },
  generating_followup: {
    icon: MessageSquare,
    label: '추가 질문 생성',
    color: 'text-blue-500',
  },
  advancing_stage: { icon: Target, label: '단계 진행', color: 'text-green-500' },
  compiling_context: {
    icon: BarChart3,
    label: '결과 정리',
    color: 'text-indigo-500',
  },
  web_searching: { icon: Search, label: '웹 검색', color: 'text-cyan-500' },
  web_search_result: {
    icon: Search,
    label: '검색 완료',
    color: 'text-cyan-500',
  },
  analyzing_goals: { icon: Target, label: '목표 분석', color: 'text-orange-500' },
  goals_analyzed: { icon: Target, label: '목표 분석 완료', color: 'text-green-500' },
  generating_monthly: {
    icon: Calendar,
    label: '월간 계획',
    color: 'text-blue-500',
  },
  monthly_generated: {
    icon: Calendar,
    label: '월간 계획 완료',
    color: 'text-green-500',
  },
  generating_weekly: {
    icon: Calendar,
    label: '주간 계획',
    color: 'text-blue-500',
  },
  weekly_generated: {
    icon: Calendar,
    label: '주간 계획 완료',
    color: 'text-green-500',
  },
  generating_daily: {
    icon: Calendar,
    label: '일일 계획',
    color: 'text-blue-500',
  },
  daily_generated: {
    icon: Calendar,
    label: '일일 계획 완료',
    color: 'text-green-500',
  },
  validating: { icon: CheckCircle2, label: '검증', color: 'text-yellow-500' },
  saving: { icon: Loader2, label: '저장', color: 'text-gray-500' },
};

function EventIcon({ type, className }: { type: StreamEventType; className?: string }) {
  const config = EVENT_CONFIG[type] || EVENT_CONFIG.progress;
  const Icon = config.icon;
  return <Icon className={cn('h-4 w-4', config.color, className)} />;
}

export function StreamingProgress({
  events,
  currentEvent,
  progress,
  isStreaming,
  error,
  className,
}: StreamingProgressProps) {
  const [visibleEvents, setVisibleEvents] = useState<StreamEvent[]>([]);

  // Animate events appearing
  useEffect(() => {
    if (events.length > visibleEvents.length) {
      const timer = setTimeout(() => {
        setVisibleEvents(events.slice(0, visibleEvents.length + 1));
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [events, visibleEvents.length]);

  // Reset when streaming starts
  useEffect(() => {
    if (isStreaming && events.length === 0) {
      setVisibleEvents([]);
    }
  }, [isStreaming, events.length]);

  const progressBarColor = useMemo(() => {
    if (error) return 'bg-red-500';
    if (progress === 100) return 'bg-green-500';
    return 'bg-primary-500';
  }, [error, progress]);

  if (!isStreaming && events.length === 0 && !error) {
    return null;
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Progress Bar */}
      <div className="relative">
        <div className="h-2 bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-500 ease-out',
              progressBarColor
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-1 flex justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>{progress}%</span>
          <span>
            {currentEvent?.message || (isStreaming ? '준비 중...' : '')}
          </span>
        </div>
      </div>

      {/* Current Action */}
      {currentEvent && isStreaming && (
        <div
          className={cn(
            'flex items-center gap-3 p-4 rounded-xl',
            'bg-primary-50 dark:bg-primary-500/10',
            'border border-primary-200 dark:border-primary-500/30',
            'animate-pulse'
          )}
        >
          <div className="relative">
            <EventIcon type={currentEvent.type} className="h-6 w-6" />
            {currentEvent.type !== 'complete' &&
              currentEvent.type !== 'error' && (
                <Loader2 className="absolute -top-1 -right-1 h-3 w-3 animate-spin text-primary-500" />
              )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-medium text-gray-900 dark:text-white">
              {currentEvent.message}
            </div>
            {currentEvent.data && (
              <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
                {formatEventData(currentEvent.data)}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Event Timeline */}
      {visibleEvents.length > 0 && (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {visibleEvents.map((event, index) => (
            <div
              key={index}
              className={cn(
                'flex items-center gap-2 text-sm transition-opacity duration-300',
                index === visibleEvents.length - 1
                  ? 'opacity-100'
                  : 'opacity-60'
              )}
            >
              <EventIcon type={event.type} />
              <span className="text-gray-700 dark:text-gray-300">
                {event.message}
              </span>
              {event.type === 'web_search_result' && event.data?.count && (
                <span className="px-1.5 py-0.5 text-xs bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400 rounded">
                  {event.data.count}개 발견
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div
          className={cn(
            'flex items-center gap-3 p-4 rounded-xl',
            'bg-red-50 dark:bg-red-500/10',
            'border border-red-200 dark:border-red-500/30'
          )}
        >
          <AlertCircle className="h-6 w-6 text-red-500" />
          <div>
            <div className="font-medium text-red-700 dark:text-red-400">
              오류가 발생했습니다
            </div>
            <div className="text-sm text-red-600 dark:text-red-300">{error}</div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatEventData(data: Record<string, unknown>): string {
  if (data.count) return `${data.count}개 항목`;
  if (data.stage) return `Stage ${data.stage}`;
  if (data.month && data.total) return `${data.month}/${data.total}`;
  if (data.week && data.total) return `${data.week}/${data.total}`;
  if (data.titles) return (data.titles as string[]).join(', ');
  return '';
}

// Simplified inline progress for compact spaces
export function StreamingProgressInline({
  currentEvent,
  progress,
  isStreaming,
}: {
  currentEvent: StreamEvent | null;
  progress: number;
  isStreaming: boolean;
}) {
  if (!isStreaming) return null;

  return (
    <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
      <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
      <span>{currentEvent?.message || '처리 중...'}</span>
      <span className="text-xs">({progress}%)</span>
    </div>
  );
}
