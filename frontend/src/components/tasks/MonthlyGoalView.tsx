import { useState } from 'react';
import { ChevronDown, ChevronRight, Target } from 'lucide-react';
import { Progress, CircularProgress } from '@/components/common/Progress';
import { WeeklyTaskView } from './WeeklyTaskView';
import { cn } from '@/lib/utils';
import type { MonthlyGoalWithWeekly } from '@/types';

interface MonthlyGoalViewProps {
  month: MonthlyGoalWithWeekly;
  mode: 'planning' | 'learning';
  defaultExpanded?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
}

export function MonthlyGoalView({
  month,
  mode,
  defaultExpanded = false,
  onToggleDailyTask,
  onStartQuiz,
}: MonthlyGoalViewProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Calculate progress from weekly tasks
  const allDailyTasks = month.weekly_tasks?.flatMap(w => w.daily_tasks || []) || [];
  const completedCount = allDailyTasks.filter(t => t.is_checked).length;
  const totalCount = allDailyTasks.length;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : (month.progress || 0);

  return (
    <div className="bg-white dark:bg-dark-800 rounded-xl border border-gray-200 dark:border-dark-600 overflow-hidden shadow-sm">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-4 p-5 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors text-left"
      >
        <div className="flex-shrink-0">
          <CircularProgress value={progress} size={60} strokeWidth={5} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Target className="h-4 w-4 text-primary-600 dark:text-primary-400" />
            <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
              {month.month_number}월차 목표
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
            {month.title}
          </h3>
          {month.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate mt-1">
              {month.description}
            </p>
          )}
        </div>

        <div className="flex-shrink-0 text-gray-400 dark:text-gray-500">
          {isExpanded ? (
            <ChevronDown className="h-6 w-6" />
          ) : (
            <ChevronRight className="h-6 w-6" />
          )}
        </div>
      </button>

      {/* Weekly Tasks */}
      {isExpanded && month.weekly_tasks && (
        <div className="border-t border-gray-200 dark:border-dark-600 bg-gray-50 dark:bg-dark-900 p-4 space-y-3">
          {month.weekly_tasks.map((week, index) => (
            <WeeklyTaskView
              key={week.id}
              week={week}
              mode={mode}
              defaultExpanded={index === 0}
              onToggleDailyTask={onToggleDailyTask}
              onStartQuiz={onStartQuiz}
            />
          ))}
        </div>
      )}
    </div>
  );
}
