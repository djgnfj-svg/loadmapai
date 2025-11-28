import { useState } from 'react';
import { ChevronDown, Calendar, CheckCircle2 } from 'lucide-react';
import { Progress } from '@/components/common/Progress';
import { DailyTaskView } from './DailyTaskView';
import { cn } from '@/lib/utils';
import type { WeeklyTaskWithDaily } from '@/types';

interface WeeklyTaskViewProps {
  week: WeeklyTaskWithDaily;
  mode: 'planning' | 'learning';
  defaultExpanded?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
}

export function WeeklyTaskView({
  week,
  mode,
  defaultExpanded = false,
  onToggleDailyTask,
  onStartQuiz,
}: WeeklyTaskViewProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const completedCount = week.daily_tasks?.filter(t => t.is_checked).length || 0;
  const totalCount = week.daily_tasks?.length || 0;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const isComplete = progress === 100;

  // Mode-specific styles
  const modeStyles = {
    planning: {
      border: 'border-primary-200 dark:border-primary-500/30',
      borderHover: 'hover:border-primary-300 dark:hover:border-primary-500/50',
      borderExpanded: 'border-primary-400 dark:border-primary-500/60',
      progress: 'primary' as const,
      accentBg: 'bg-primary-50 dark:bg-primary-500/10',
    },
    learning: {
      border: 'border-emerald-200 dark:border-emerald-500/30',
      borderHover: 'hover:border-emerald-300 dark:hover:border-emerald-500/50',
      borderExpanded: 'border-emerald-400 dark:border-emerald-500/60',
      progress: 'success' as const,
      accentBg: 'bg-emerald-50 dark:bg-emerald-500/10',
    },
  };

  const currentMode = modeStyles[mode];

  return (
    <div
      className={cn(
        'rounded-xl overflow-hidden transition-all duration-300 border-2',
        'bg-white dark:bg-dark-800',
        isExpanded
          ? cn(currentMode.borderExpanded, 'shadow-md')
          : cn(currentMode.border, currentMode.borderHover, 'shadow-sm hover:shadow-md')
      )}
    >
      {/* Horizontal Card Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left"
      >
        <div className="p-4">
          <div className="flex items-center gap-4">
            {/* Week Number Badge */}
            <div className={cn(
              'flex-shrink-0 w-14 h-14 rounded-xl flex flex-col items-center justify-center',
              currentMode.accentBg
            )}>
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Week</span>
              <span className={cn(
                'text-xl font-bold',
                mode === 'planning' ? 'text-primary-600 dark:text-primary-400' : 'text-emerald-600 dark:text-emerald-400'
              )}>
                {week.week_number}
              </span>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                  {week.title}
                </h4>
                {isComplete && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400">
                    <CheckCircle2 className="h-3 w-3" />
                    완료
                  </span>
                )}
              </div>
              {week.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                  {week.description}
                </p>
              )}
            </div>

            {/* Progress and Stats */}
            <div className="flex-shrink-0 flex items-center gap-4">
              <div className="hidden sm:flex flex-col items-end gap-1">
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {completedCount}/{totalCount}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">완료</span>
              </div>
              <div className="w-20">
                <Progress value={progress} size="md" color={currentMode.progress} />
                <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {progress}%
                </div>
              </div>
              <div className={cn(
                'flex-shrink-0 p-2 rounded-full transition-all duration-300',
                isExpanded
                  ? cn(currentMode.accentBg, 'rotate-180')
                  : 'bg-gray-100 dark:bg-dark-700'
              )}>
                <ChevronDown className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </button>

      {/* Expanded Daily Tasks */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-300 ease-in-out',
          isExpanded ? 'max-h-[1500px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        {week.daily_tasks && week.daily_tasks.length > 0 && (
          <div className={cn(
            'px-4 pb-4 pt-2',
            currentMode.accentBg
          )}>
            {/* Section Divider */}
            <div className="flex items-center gap-2 mb-3">
              <div className={cn(
                'h-px flex-1',
                mode === 'planning' ? 'bg-primary-200 dark:bg-primary-500/30' : 'bg-emerald-200 dark:bg-emerald-500/30'
              )} />
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                일별 태스크
              </span>
              <div className={cn(
                'h-px flex-1',
                mode === 'planning' ? 'bg-primary-200 dark:bg-primary-500/30' : 'bg-emerald-200 dark:bg-emerald-500/30'
              )} />
            </div>

            {/* Daily Tasks Grid */}
            <div className="grid gap-2">
              {week.daily_tasks.map((task) => (
                <DailyTaskView
                  key={task.id}
                  task={task}
                  mode={mode}
                  onToggle={onToggleDailyTask}
                  onStartQuiz={onStartQuiz}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
