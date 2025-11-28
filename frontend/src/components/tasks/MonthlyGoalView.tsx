import { useState } from 'react';
import { ChevronDown, Calendar, CheckCircle2, Pencil } from 'lucide-react';
import { addMonths, format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { CircularProgress } from '@/components/common/Progress';
import { WeeklyTaskView } from './WeeklyTaskView';
import { cn } from '@/lib/utils';
import type { MonthlyGoalWithWeekly, DailyTask, WeeklyTask, MonthlyGoal } from '@/types';

interface MonthlyGoalViewProps {
  month: MonthlyGoalWithWeekly;
  mode: 'planning' | 'learning';
  startDate: string;
  defaultExpanded?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
  isEditable?: boolean;
  onEditDailyTask?: (task: DailyTask, weeklyTaskId: string) => void;
  onEditWeeklyTask?: (task: WeeklyTask, monthlyGoalId: string) => void;
  onEditMonthlyGoal?: (goal: MonthlyGoal) => void;
}

export function MonthlyGoalView({
  month,
  mode,
  startDate,
  defaultExpanded = false,
  onToggleDailyTask,
  onStartQuiz,
  isEditable = false,
  onEditDailyTask,
  onEditWeeklyTask,
  onEditMonthlyGoal,
}: MonthlyGoalViewProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Calculate actual calendar month
  const actualMonth = addMonths(new Date(startDate), month.month_number - 1);
  const monthLabel = format(actualMonth, 'M월', { locale: ko });

  // Calculate progress from weekly tasks
  const allDailyTasks = month.weekly_tasks?.flatMap(w => w.daily_tasks || []) || [];
  const completedCount = allDailyTasks.filter(t => t.is_checked).length;
  const totalCount = allDailyTasks.length;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : (month.progress || 0);
  const weekCount = month.weekly_tasks?.length || 0;

  const isComplete = progress === 100;

  // Mode-specific styles
  const modeStyles = {
    planning: {
      accent: 'from-primary-500 to-indigo-600',
      accentLight: 'from-primary-500/20 to-indigo-600/20',
      badge: 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400',
    },
    learning: {
      accent: 'from-emerald-500 to-teal-600',
      accentLight: 'from-emerald-500/20 to-teal-600/20',
      badge: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
    },
  };

  const currentMode = modeStyles[mode];

  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden transition-all duration-300',
        isExpanded
          ? 'bg-white dark:bg-dark-800 shadow-xl shadow-gray-200/50 dark:shadow-dark-900/50 ring-2 ring-gray-200 dark:ring-dark-600'
          : 'bg-white dark:bg-dark-800 shadow-md hover:shadow-lg border border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
      )}
    >
      {/* Gradient Top Bar */}
      <div className={cn('h-1.5 bg-gradient-to-r', currentMode.accent)} />

      {/* Header Card */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left"
      >
        <div className="p-5">
          <div className="flex items-start gap-4">
            {/* Progress Circle */}
            <div className="flex-shrink-0 relative">
              <CircularProgress
                value={progress}
                size={72}
                strokeWidth={6}
                color={mode === 'learning' ? 'success' : 'primary'}
              />
              {isComplete && (
                <div className="absolute -top-1 -right-1 bg-green-500 rounded-full p-1">
                  <CheckCircle2 className="h-4 w-4 text-white" />
                </div>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                {/* Month Badge - Actual Calendar Month */}
                <span className={cn(
                  'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold',
                  currentMode.badge
                )}>
                  <Calendar className="h-3 w-3" />
                  {monthLabel}
                </span>
                {/* Month Number Badge */}
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400">
                  {month.month_number}월차
                </span>
              </div>

              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                {month.title}
              </h3>

              {month.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                  {month.description}
                </p>
              )}

              {/* Stats Row */}
              <div className="flex items-center gap-4 mt-3 text-sm">
                <span className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                  <Calendar className="h-4 w-4" />
                  {weekCount}주 과정
                </span>
                <span className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                  <CheckCircle2 className="h-4 w-4" />
                  {completedCount}/{totalCount} 완료
                </span>
              </div>
            </div>

            {/* Edit & Expand Icons */}
            <div className="flex items-center gap-2">
              {isEditable && onEditMonthlyGoal && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEditMonthlyGoal(month);
                  }}
                  className={cn(
                    'p-2 rounded-full transition-all duration-200',
                    'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200',
                    'hover:bg-gray-100 dark:hover:bg-dark-600'
                  )}
                >
                  <Pencil className="h-4 w-4" />
                </button>
              )}
              <div className={cn(
                'flex-shrink-0 p-2 rounded-full transition-all duration-300',
                isExpanded
                  ? 'bg-gray-100 dark:bg-dark-700 rotate-180'
                  : 'bg-gray-50 dark:bg-dark-700'
              )}>
                <ChevronDown className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      </button>

      {/* Expanded Weekly Tasks */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-300 ease-in-out',
          isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        {month.weekly_tasks && month.weekly_tasks.length > 0 && (
          <div className={cn(
            'px-5 pb-5 pt-2 space-y-3 bg-gradient-to-b',
            currentMode.accentLight
          )}>
            {/* Section Header */}
            <div className="flex items-center gap-2 mb-4">
              <div className={cn('h-0.5 flex-1 bg-gradient-to-r', currentMode.accent, 'opacity-30')} />
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                주간 계획
              </span>
              <div className={cn('h-0.5 flex-1 bg-gradient-to-l', currentMode.accent, 'opacity-30')} />
            </div>

            {month.weekly_tasks.map((week) => (
              <WeeklyTaskView
                key={week.id}
                week={week}
                mode={mode}
                defaultExpanded={false}
                onToggleDailyTask={onToggleDailyTask}
                onStartQuiz={onStartQuiz}
                isEditable={isEditable}
                onEditDailyTask={onEditDailyTask}
                onEditWeeklyTask={(task) => onEditWeeklyTask?.(task, month.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
