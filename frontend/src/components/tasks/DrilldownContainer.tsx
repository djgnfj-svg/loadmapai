import { MonthlyGoalView } from './MonthlyGoalView';
import { Skeleton } from '@/components/common/Loading';
import type { RoadmapFull } from '@/types';

interface DrilldownContainerProps {
  roadmap: RoadmapFull;
  isLoading?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
}

export function DrilldownContainer({
  roadmap,
  isLoading,
  onToggleDailyTask,
  onStartQuiz,
}: DrilldownContainerProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-5">
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
      <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
        <p className="text-gray-500">아직 월별 목표가 없습니다.</p>
      </div>
    );
  }

  // Find the current month based on progress or default to first incomplete
  const currentMonthIndex = roadmap.monthly_goals.findIndex((m) => {
    const allDailyTasks = m.weekly_tasks?.flatMap(w => w.daily_tasks || []) || [];
    const completedCount = allDailyTasks.filter(t => t.is_checked).length;
    return completedCount < allDailyTasks.length;
  });

  return (
    <div className="space-y-4">
      {roadmap.monthly_goals.map((month, index) => (
        <MonthlyGoalView
          key={month.id}
          month={month}
          mode={roadmap.mode}
          defaultExpanded={index === currentMonthIndex || index === 0}
          onToggleDailyTask={onToggleDailyTask}
          onStartQuiz={onStartQuiz}
        />
      ))}
    </div>
  );
}
