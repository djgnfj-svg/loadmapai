import { useState, useMemo } from 'react';
import { ChevronDown, Calendar, CheckCircle2, Pencil } from 'lucide-react';
import { Progress } from '@/components/common/Progress';
import { DayGroupView } from './DayGroupView';
import { cn } from '@/lib/utils';
import type { WeeklyTaskWithDaily, DailyTask, WeeklyTask } from '@/types';

interface WeeklyTaskViewProps {
  week: WeeklyTaskWithDaily;
  defaultExpanded?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  isEditable?: boolean;
  onEditDailyTask?: (task: DailyTask, weeklyTaskId: string) => void;
  onEditWeeklyTask?: (task: WeeklyTask) => void;
}

export function WeeklyTaskView({
  week,
  defaultExpanded = false,
  onToggleDailyTask,
  isEditable = false,
  onEditDailyTask,
  onEditWeeklyTask,
}: WeeklyTaskViewProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const completedCount = week.daily_tasks?.filter(t => t.is_checked).length || 0;
  const totalCount = week.daily_tasks?.length || 0;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const isComplete = progress === 100;

  // Group daily tasks by day_number
  const tasksByDay = useMemo(() => {
    if (!week.daily_tasks) return [];

    const grouped = week.daily_tasks.reduce((acc, task) => {
      const dayNum = task.day_number;
      if (!acc[dayNum]) {
        acc[dayNum] = [];
      }
      acc[dayNum].push(task);
      return acc;
    }, {} as Record<number, DailyTask[]>);

    // Sort by day number and return as array
    return Object.entries(grouped)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([dayNumber, tasks]) => ({
        dayNumber: Number(dayNumber),
        tasks: tasks.sort((a, b) => a.order - b.order),
      }));
  }, [week.daily_tasks]);

  return (
    <div
      className={cn(
        'rounded-xl overflow-hidden transition-all duration-300 border-2',
        'bg-white dark:bg-dark-800',
        isExpanded
          ? 'border-primary-400 dark:border-primary-500/60 shadow-md'
          : 'border-primary-200 dark:border-primary-500/30 hover:border-primary-300 dark:hover:border-primary-500/50 shadow-sm hover:shadow-md'
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
            <div className="flex-shrink-0 w-14 h-14 rounded-xl flex flex-col items-center justify-center bg-primary-50 dark:bg-primary-500/10">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Week</span>
              <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
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
                <Progress value={progress} size="md" color="primary" />
                <div className="text-center text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {progress}%
                </div>
              </div>
              <div className="flex items-center gap-1">
                {isEditable && onEditWeeklyTask && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditWeeklyTask(week);
                    }}
                    className={cn(
                      'p-1.5 rounded-lg transition-all duration-200',
                      'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200',
                      'hover:bg-gray-100 dark:hover:bg-dark-600'
                    )}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                )}
                <div className={cn(
                  'flex-shrink-0 p-2 rounded-full transition-all duration-300',
                  isExpanded
                    ? 'bg-primary-50 dark:bg-primary-500/10 rotate-180'
                    : 'bg-gray-100 dark:bg-dark-700'
                )}>
                  <ChevronDown className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </button>

      {/* Expanded Daily Tasks */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-300 ease-in-out',
          isExpanded ? 'max-h-[3000px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        {tasksByDay.length > 0 && (
          <div className="px-4 pb-4 pt-2 bg-primary-50 dark:bg-primary-500/10">
            {/* Section Divider */}
            <div className="flex items-center gap-2 mb-3">
              <div className="h-px flex-1 bg-primary-200 dark:bg-primary-500/30" />
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                일별 태스크
              </span>
              <div className="h-px flex-1 bg-primary-200 dark:bg-primary-500/30" />
            </div>

            {/* Daily Tasks by Day */}
            <div className="grid gap-2">
              {tasksByDay.map(({ dayNumber, tasks }) => (
                <DayGroupView
                  key={dayNumber}
                  dayNumber={dayNumber}
                  tasks={tasks}
                  defaultExpanded={false}
                  onToggleTask={onToggleDailyTask}
                  isEditable={isEditable}
                  onEditTask={(t) => onEditDailyTask?.(t, week.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
