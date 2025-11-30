import { MonthlyGoalView } from './MonthlyGoalView';
import { Skeleton } from '@/components/common';
import type { RoadmapFull, DailyTask, WeeklyTask, MonthlyGoal } from '@/types';

interface DrilldownContainerProps {
  roadmap: RoadmapFull;
  isLoading?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  isEditable?: boolean;
  onEditDailyTask?: (task: DailyTask, weeklyTaskId: string) => void;
  onEditWeeklyTask?: (task: WeeklyTask, monthlyGoalId: string) => void;
  onEditMonthlyGoal?: (goal: MonthlyGoal) => void;
}

export function DrilldownContainer({
  roadmap,
  isLoading,
  onToggleDailyTask,
  isEditable = false,
  onEditDailyTask,
  onEditWeeklyTask,
  onEditMonthlyGoal,
}: DrilldownContainerProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white dark:bg-dark-800 rounded-xl border border-gray-200 dark:border-dark-600 p-5">
            <div className="flex items-center gap-4">
              <Skeleton className="h-16 w-16 rounded-full" />
              <div className="flex-1">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-6 w-48 mb-2" />
                <Skeleton className="h-4 w-64" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!roadmap.monthly_goals || roadmap.monthly_goals.length === 0) {
    return (
      <div className="text-center py-12 bg-white dark:bg-dark-800 rounded-xl border border-gray-200 dark:border-dark-600">
        <p className="text-gray-500 dark:text-gray-400">아직 월별 목표가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {roadmap.monthly_goals.map((month) => (
        <MonthlyGoalView
          key={month.id}
          month={month}
          startDate={roadmap.start_date}
          defaultExpanded={false}
          onToggleDailyTask={onToggleDailyTask}
          isEditable={isEditable}
          onEditDailyTask={onEditDailyTask}
          onEditWeeklyTask={onEditWeeklyTask}
          onEditMonthlyGoal={onEditMonthlyGoal}
        />
      ))}
    </div>
  );
}
