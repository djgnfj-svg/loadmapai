import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, Calendar, CheckCircle2, Pencil, Sparkles, Loader2, Lock, BookOpen, Play } from 'lucide-react';
import { Progress } from '@/components/common/Progress';
import { DayGroupView } from './DayGroupView';
import { cn } from '@/lib/utils';
import type { WeeklyTaskWithDaily, DailyTask, DailyGoal, WeeklyTask, RoadmapMode } from '@/types';

interface WeeklyTaskViewProps {
  week: WeeklyTaskWithDaily;
  roadmapId: string;
  defaultExpanded?: boolean;
  onToggleDailyTask: (taskId: string) => void;
  isEditable?: boolean;
  onEditDailyTask?: (task: DailyTask, weeklyTaskId: string) => void;
  onEditWeeklyTask?: (task: WeeklyTask) => void;
  onGenerateDailyTasks?: (weeklyTaskId: string) => void;
  isGenerating?: boolean;
  canGenerate?: boolean;
  cannotGenerateReason?: string | null;
  mode?: RoadmapMode;
}

export function WeeklyTaskView({
  week,
  roadmapId,
  defaultExpanded = false,
  onToggleDailyTask,
  isEditable = false,
  onEditDailyTask,
  onEditWeeklyTask,
  onGenerateDailyTasks,
  isGenerating = false,
  canGenerate = true,
  cannotGenerateReason = null,
  mode = 'PLANNING',
}: WeeklyTaskViewProps) {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const isLearningMode = mode === 'LEARNING';

  // DB에서 가져온 생성 상태도 확인 (새로고침해도 유지됨)
  const isGeneratingFromDB = week.daily_generation_status === 'generating';
  const actualIsGenerating = isGenerating || isGeneratingFromDB;

  const completedCount = week.daily_tasks?.filter(t => t.is_checked).length || 0;
  const totalCount = week.daily_tasks?.length || 0;
  const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
  const isComplete = progress === 100;

  // Create a map of daily goals by day_number
  const goalsByDay = useMemo(() => {
    if (!week.daily_goals) return {} as Record<number, DailyGoal>;
    return week.daily_goals.reduce((acc, goal) => {
      acc[goal.day_number] = goal;
      return acc;
    }, {} as Record<number, DailyGoal>);
  }, [week.daily_goals]);

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
        goal: goalsByDay[Number(dayNumber)],
        tasks: tasks.sort((a, b) => a.order - b.order),
      }));
  }, [week.daily_tasks, goalsByDay]);

  // Navigate to learning page
  const handleStartLearning = (dailyTaskId: string) => {
    navigate(`/roadmaps/${roadmapId}/learn/${dailyTaskId}`);
  };

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
          isExpanded ? 'max-h-[10000px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        {tasksByDay.length > 0 ? (
          <div className="px-4 pb-4 pt-2 bg-primary-50 dark:bg-primary-500/10">
            {/* Section Divider */}
            <div className="flex items-center gap-2 mb-3">
              <div className="h-px flex-1 bg-primary-200 dark:bg-primary-500/30" />
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center gap-1">
                {isLearningMode ? (
                  <>
                    <BookOpen className="h-3 w-3" />
                    일별 학습
                  </>
                ) : (
                  <>
                    <Calendar className="h-3 w-3" />
                    일별 태스크
                  </>
                )}
              </span>
              <div className="h-px flex-1 bg-primary-200 dark:bg-primary-500/30" />
            </div>

            {/* Daily Tasks/Learning by Day */}
            <div className="grid gap-2">
              {isLearningMode ? (
                // LEARNING MODE: Show day cards that navigate to learning page
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
                  {tasksByDay.map(({ dayNumber, goal, tasks }) => {
                    const dailyTask = tasks[0];
                    const isCompleted = dailyTask?.is_checked;

                    return (
                      <button
                        key={dayNumber}
                        onClick={() => handleStartLearning(dailyTask.id)}
                        className={cn(
                          'flex flex-col items-center justify-center p-4 rounded-xl transition-all',
                          'border-2 group',
                          isCompleted
                            ? 'border-green-500 bg-green-50 dark:bg-green-500/10'
                            : 'border-gray-200 dark:border-dark-600 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-white dark:hover:bg-dark-700',
                          'hover:shadow-lg hover:scale-105'
                        )}
                      >
                        <span className="text-xs text-gray-500 dark:text-gray-400 mb-1">Day</span>
                        <span className={cn(
                          'text-2xl font-bold mb-2',
                          isCompleted
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-gray-900 dark:text-white'
                        )}>
                          {dayNumber}
                        </span>
                        {isCompleted ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500" />
                        ) : (
                          <div className="flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Play className="h-3 w-3" />
                            <span>시작</span>
                          </div>
                        )}
                        {goal?.title && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center line-clamp-2">
                            {goal.title}
                          </p>
                        )}
                      </button>
                    );
                  })}
                </div>
              ) : (
                // PLANNING MODE: Show DayGroupView
                tasksByDay.map(({ dayNumber, goal, tasks }) => (
                  <DayGroupView
                    key={dayNumber}
                    dayNumber={dayNumber}
                    goal={goal}
                    tasks={tasks}
                    defaultExpanded={false}
                    onToggleTask={onToggleDailyTask}
                    isEditable={isEditable}
                    onEditTask={(t) => onEditDailyTask?.(t, week.id)}
                  />
                ))
              )}
            </div>
          </div>
        ) : (
          <div className="px-4 pb-4 pt-2 bg-primary-50 dark:bg-primary-500/10">
            {/* No Daily Tasks - Generate Button or Locked State */}
            <div className="flex flex-col items-center justify-center py-8 text-center">
              {canGenerate ? (
                <>
                  <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-500/20 flex items-center justify-center mb-3">
                    <Calendar className="h-6 w-6 text-primary-500 dark:text-primary-400" />
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    이 주차의 일일 태스크가 아직 생성되지 않았습니다.
                  </p>
                  {onGenerateDailyTasks && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onGenerateDailyTasks(week.id);
                      }}
                      disabled={actualIsGenerating}
                      className={cn(
                        'flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all',
                        'bg-primary-500 hover:bg-primary-600 text-white',
                        'disabled:opacity-50 disabled:cursor-not-allowed'
                      )}
                    >
                      {actualIsGenerating ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          생성 중...
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4" />
                          일일 태스크 생성하기
                        </>
                      )}
                    </button>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                    이전 주차를 완료하면 자동으로 생성됩니다.
                  </p>
                </>
              ) : (
                <>
                  <div className="w-12 h-12 rounded-full bg-gray-200 dark:bg-dark-600 flex items-center justify-center mb-3">
                    <Lock className="h-6 w-6 text-gray-400 dark:text-gray-500" />
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {cannotGenerateReason || '이전 주차를 먼저 완료해주세요.'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    이전 주차의 모든 태스크를 완료하면 잠금이 해제됩니다.
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
