import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
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

  return (
    <div className="border border-gray-200 dark:border-dark-600 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-3 p-4 bg-white dark:bg-dark-800 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors text-left"
      >
        <div className="flex-shrink-0 text-gray-400 dark:text-gray-500">
          {isExpanded ? (
            <ChevronDown className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-500/20 px-2 py-0.5 rounded">
              Week {week.week_number}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {completedCount}/{totalCount} 완료
            </span>
          </div>
          <h4 className="font-medium text-gray-900 dark:text-white truncate">
            {week.title}
          </h4>
        </div>

        <div className="flex-shrink-0 w-24">
          <Progress value={progress} size="sm" />
        </div>
      </button>

      {/* Daily Tasks */}
      {isExpanded && week.daily_tasks && (
        <div className="border-t border-gray-200 dark:border-dark-600 bg-gray-50/50 dark:bg-dark-900/50 p-3 space-y-2">
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
      )}
    </div>
  );
}
