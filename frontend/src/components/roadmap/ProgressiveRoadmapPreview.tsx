import { useMemo } from 'react';
import {
  Calendar,
  ChevronDown,
  ChevronRight,
  Target,
  Clock,
  BookOpen,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PartialRoadmap } from '@/hooks/useStreaming';

interface ProgressiveRoadmapPreviewProps {
  partialRoadmap: PartialRoadmap;
  isStreaming: boolean;
  className?: string;
}

export function ProgressiveRoadmapPreview({
  partialRoadmap,
  isStreaming,
  className,
}: ProgressiveRoadmapPreviewProps) {
  const { title, description, monthly_goals, weekly_tasks, daily_tasks } = partialRoadmap;

  const hasContent = title || monthly_goals.length > 0;

  if (!hasContent && !isStreaming) {
    return null;
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Title Section */}
      {title ? (
        <div className="animate-fade-in">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Target className="h-5 w-5 text-primary-500" />
            {title}
          </h3>
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
      ) : isStreaming ? (
        <div className="flex items-center gap-2 text-gray-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">로드맵 제목 생성 중...</span>
        </div>
      ) : null}

      {/* Monthly Goals */}
      <div className="space-y-3">
        {monthly_goals.map((month, idx) => (
          <MonthCard
            key={month.month_number}
            month={month}
            weeklyTasks={weekly_tasks.get(month.month_number) || []}
            dailyTasks={daily_tasks}
            isLatest={idx === monthly_goals.length - 1 && isStreaming}
          />
        ))}

        {/* Placeholder for upcoming months */}
        {isStreaming && monthly_goals.length > 0 && (
          <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 dark:bg-dark-700 rounded-lg border border-dashed border-gray-200 dark:border-dark-500">
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
            <span className="text-sm text-gray-400">다음 월간 계획 생성 중...</span>
          </div>
        )}
      </div>
    </div>
  );
}

interface MonthCardProps {
  month: {
    month_number: number;
    title: string;
    description: string;
  };
  weeklyTasks: Array<{
    week_number: number;
    title: string;
    description: string;
  }>;
  dailyTasks: Map<string, Array<{
    day_number: number;
    title: string;
    description: string;
  }>>;
  isLatest: boolean;
}

function MonthCard({ month, weeklyTasks, dailyTasks, isLatest }: MonthCardProps) {
  const sortedWeeks = useMemo(
    () => [...weeklyTasks].sort((a, b) => a.week_number - b.week_number),
    [weeklyTasks]
  );

  return (
    <div
      className={cn(
        'rounded-xl border overflow-hidden transition-all duration-500',
        isLatest
          ? 'border-primary-300 dark:border-primary-500/50 bg-primary-50/50 dark:bg-primary-500/5 animate-fade-in'
          : 'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800'
      )}
    >
      {/* Month Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-500/10 dark:to-transparent border-b border-gray-100 dark:border-dark-600">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-500/20">
            <Calendar className="h-4 w-4 text-primary-600 dark:text-primary-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-gray-900 dark:text-white">
              {month.month_number}월: {month.title}
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {month.description}
            </p>
          </div>
          {isLatest && (
            <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
          )}
        </div>
      </div>

      {/* Weekly Tasks */}
      {sortedWeeks.length > 0 && (
        <div className="divide-y divide-gray-100 dark:divide-dark-600">
          {sortedWeeks.map((week, weekIdx) => {
            const key = `${month.month_number}_${week.week_number}`;
            const dayTasks = dailyTasks.get(key) || [];
            const isLatestWeek = isLatest && weekIdx === sortedWeeks.length - 1;

            return (
              <WeekRow
                key={week.week_number}
                week={week}
                dailyTasks={dayTasks}
                isLatest={isLatestWeek}
              />
            );
          })}
        </div>
      )}

      {/* Loading state for weeks */}
      {isLatest && sortedWeeks.length === 0 && (
        <div className="px-4 py-3 flex items-center gap-2 text-gray-400">
          <Clock className="h-4 w-4 animate-pulse" />
          <span className="text-sm">주간 계획 생성 대기 중...</span>
        </div>
      )}
    </div>
  );
}

interface WeekRowProps {
  week: {
    week_number: number;
    title: string;
    description: string;
  };
  dailyTasks: Array<{
    day_number: number;
    title: string;
    description: string;
  }>;
  isLatest: boolean;
}

function WeekRow({ week, dailyTasks, isLatest }: WeekRowProps) {
  const sortedDays = useMemo(
    () => [...dailyTasks].sort((a, b) => a.day_number - b.day_number),
    [dailyTasks]
  );

  return (
    <div
      className={cn(
        'transition-all duration-300',
        isLatest ? 'animate-fade-in bg-primary-50/30 dark:bg-primary-500/5' : ''
      )}
    >
      {/* Week Header */}
      <div className="px-4 py-2 flex items-center gap-2">
        <ChevronRight className="h-4 w-4 text-gray-400" />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {week.week_number}주차: {week.title}
          </span>
        </div>
        {isLatest && dailyTasks.length === 0 && (
          <Loader2 className="h-3 w-3 animate-spin text-primary-400" />
        )}
      </div>

      {/* Daily Tasks (collapsed view) */}
      {sortedDays.length > 0 && (
        <div className="px-4 pb-2 pl-10">
          <div className="flex flex-wrap gap-1">
            {sortedDays.map((day, dayIdx) => (
              <div
                key={day.day_number}
                className={cn(
                  'px-2 py-1 text-xs rounded-md transition-all duration-200',
                  'bg-gray-100 dark:bg-dark-600 text-gray-600 dark:text-gray-400',
                  isLatest && dayIdx === sortedDays.length - 1
                    ? 'animate-fade-in ring-1 ring-primary-300 dark:ring-primary-500/50'
                    : ''
                )}
                title={day.description}
              >
                <BookOpen className="inline h-3 w-3 mr-1" />
                D{day.day_number}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Add to your global CSS or tailwind config
// @keyframes fade-in {
//   from { opacity: 0; transform: translateY(-4px); }
//   to { opacity: 1; transform: translateY(0); }
// }
// .animate-fade-in { animation: fade-in 0.3s ease-out forwards; }
