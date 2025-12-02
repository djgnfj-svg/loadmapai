import { useParams, useNavigate, Link } from 'react-router-dom';
import { format, differenceInDays } from 'date-fns';
import { ko } from 'date-fns/locale';
import {
  ArrowLeft,
  Calendar,
  Clock,
  MoreVertical,
  Trash2,
  Pause,
  Play,
  Map,
  Edit3,
  Lock,
  Unlock,
  AlertTriangle,
} from 'lucide-react';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  useRoadmapFull,
  useToggleDailyTask,
  useDeleteRoadmap,
  useFinalizeRoadmap,
  useUnfinalizeRoadmap,
  useUpdateDailyTask,
  useUpdateWeeklyTask,
  useUpdateMonthlyGoal,
  useDeleteDailyTask,
  useDeleteWeeklyTask,
  useDeleteMonthlyGoal,
} from '@/hooks';
import { roadmapApi } from '@/lib/api';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { CircularProgress, Progress } from '@/components/common/Progress';
import { LoadingScreen } from '@/components/common/Loading';
import { DrilldownContainer } from '@/components/tasks';
import { EditTaskModal } from '@/components/edit';
import { cn } from '@/lib/utils';
import type { DailyTask, WeeklyTask, MonthlyGoal } from '@/types';

// Edit state types
interface EditingDaily {
  task: DailyTask;
  weeklyTaskId: string;
}

interface EditingWeekly {
  task: WeeklyTask;
  monthlyGoalId: string;
}

export function RoadmapDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  // Edit modal state
  const [editingDaily, setEditingDaily] = useState<EditingDaily | null>(null);
  const [editingWeekly, setEditingWeekly] = useState<EditingWeekly | null>(null);
  const [editingMonthly, setEditingMonthly] = useState<MonthlyGoal | null>(null);

  const { data: roadmap, isLoading, error } = useRoadmapFull(id || '');
  const toggleDailyTask = useToggleDailyTask();
  const deleteRoadmap = useDeleteRoadmap();
  const queryClient = useQueryClient();

  // Edit mutations
  const finalizeRoadmap = useFinalizeRoadmap(id || '');
  const unfinalizeRoadmap = useUnfinalizeRoadmap(id || '');
  const updateDailyTask = useUpdateDailyTask(id || '');
  const updateWeeklyTask = useUpdateWeeklyTask(id || '');
  const updateMonthlyGoal = useUpdateMonthlyGoal(id || '');
  const deleteDailyTask = useDeleteDailyTask(id || '');
  const deleteWeeklyTask = useDeleteWeeklyTask(id || '');
  const deleteMonthlyGoal = useDeleteMonthlyGoal(id || '');

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => roadmapApi.update(id!, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmap', id] });
    },
  });

  const handleToggleDailyTask = (taskId: string) => {
    toggleDailyTask.mutate(taskId, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['roadmap', id, 'full'] });
      },
    });
  };

  const handleDelete = () => {
    if (window.confirm('정말 이 로드맵을 삭제하시겠습니까?')) {
      deleteRoadmap.mutate(id!, {
        onSuccess: () => {
          navigate('/roadmaps');
        },
      });
    }
  };

  // Edit handlers
  const handleEditDailyTask = (task: DailyTask, weeklyTaskId: string) => {
    setEditingDaily({ task, weeklyTaskId });
  };

  const handleEditWeeklyTask = (task: WeeklyTask, monthlyGoalId: string) => {
    setEditingWeekly({ task, monthlyGoalId });
  };

  const handleEditMonthlyGoal = (goal: MonthlyGoal) => {
    setEditingMonthly(goal);
  };

  const handleSaveDailyTask = (data: { title: string; description: string; day_number?: number }) => {
    if (!editingDaily) return;
    updateDailyTask.mutate(
      {
        weeklyId: editingDaily.weeklyTaskId,
        taskId: editingDaily.task.id,
        data: {
          title: data.title,
          description: data.description,
          day_number: data.day_number,
        },
      },
      {
        onSuccess: () => setEditingDaily(null),
      }
    );
  };

  const handleSaveWeeklyTask = (data: { title: string; description: string }) => {
    if (!editingWeekly) return;
    updateWeeklyTask.mutate(
      {
        goalId: editingWeekly.monthlyGoalId,
        taskId: editingWeekly.task.id,
        data: {
          title: data.title,
          description: data.description,
        },
      },
      {
        onSuccess: () => setEditingWeekly(null),
      }
    );
  };

  const handleSaveMonthlyGoal = (data: { title: string; description: string }) => {
    if (!editingMonthly) return;
    updateMonthlyGoal.mutate(
      {
        goalId: editingMonthly.id,
        data: {
          title: data.title,
          description: data.description,
        },
      },
      {
        onSuccess: () => setEditingMonthly(null),
      }
    );
  };

  const handleDeleteDailyTask = () => {
    if (!editingDaily) return;
    if (window.confirm('정말 이 태스크를 삭제하시겠습니까?')) {
      deleteDailyTask.mutate(
        {
          weeklyId: editingDaily.weeklyTaskId,
          taskId: editingDaily.task.id,
        },
        {
          onSuccess: () => setEditingDaily(null),
        }
      );
    }
  };

  const handleDeleteWeeklyTask = () => {
    if (!editingWeekly) return;
    if (window.confirm('정말 이 주간 태스크를 삭제하시겠습니까? 하위 일일 태스크도 모두 삭제됩니다.')) {
      deleteWeeklyTask.mutate(
        {
          goalId: editingWeekly.monthlyGoalId,
          taskId: editingWeekly.task.id,
        },
        {
          onSuccess: () => setEditingWeekly(null),
        }
      );
    }
  };

  const handleDeleteMonthlyGoal = () => {
    if (!editingMonthly) return;
    if (window.confirm('정말 이 월간 목표를 삭제하시겠습니까? 하위 모든 태스크도 삭제됩니다.')) {
      deleteMonthlyGoal.mutate(editingMonthly.id, {
        onSuccess: () => setEditingMonthly(null),
      });
    }
  };

  const handleFinalize = () => {
    if (roadmap?.is_finalized) {
      unfinalizeRoadmap.mutate();
    } else {
      finalizeRoadmap.mutate();
    }
  };

  if (isLoading) {
    return <LoadingScreen message="로드맵을 불러오는 중..." />;
  }

  if (error || !roadmap) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          로드맵을 찾을 수 없습니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          요청하신 로드맵이 존재하지 않거나 접근 권한이 없습니다.
        </p>
        <Link to="/roadmaps">
          <Button variant="primary">로드맵 목록으로</Button>
        </Link>
      </div>
    );
  }

  const startDate = new Date(roadmap.start_date);
  const endDate = new Date(roadmap.end_date);
  const today = new Date();
  const totalDays = differenceInDays(endDate, startDate);
  const elapsedDays = Math.max(0, Math.min(differenceInDays(today, startDate), totalDays));
  const daysRemaining = Math.max(0, differenceInDays(endDate, today));

  const statusColors = {
    active: 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-400',
    completed: 'bg-blue-100 dark:bg-blue-500/20 text-blue-800 dark:text-blue-400',
    paused: 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-800 dark:text-yellow-400',
  };

  const statusLabels = {
    active: '진행 중',
    completed: '완료',
    paused: '일시정지',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>뒤로</span>
        </button>

        <div className="relative">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowMenu(!showMenu)}
          >
            <MoreVertical className="h-5 w-5" />
          </Button>
          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 mt-1 w-40 bg-white dark:bg-dark-800 rounded-lg shadow-lg border border-gray-200 dark:border-dark-600 py-1 z-20">
                {roadmap.status === 'active' ? (
                  <button
                    onClick={() => {
                      updateStatusMutation.mutate('paused');
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-700 flex items-center gap-2"
                  >
                    <Pause className="h-4 w-4" />
                    일시정지
                  </button>
                ) : roadmap.status === 'paused' ? (
                  <button
                    onClick={() => {
                      updateStatusMutation.mutate('active');
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-dark-700 flex items-center gap-2"
                  >
                    <Play className="h-4 w-4" />
                    재개하기
                  </button>
                ) : null}
                <button
                  onClick={() => {
                    handleDelete();
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 flex items-center gap-2"
                >
                  <Trash2 className="h-4 w-4" />
                  삭제
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Roadmap Info Card */}
      <Card variant="bordered">
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Progress Circle */}
            <div className="flex-shrink-0 flex justify-center">
              <CircularProgress
                value={roadmap.progress || 0}
                size={140}
                strokeWidth={10}
              />
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                {/* Mode Badge */}
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400">
                  <Map className="h-4 w-4" />
                  플래닝 모드
                </span>
                {/* Status Badge */}
                <span className={cn('px-2.5 py-1 text-xs font-medium rounded-full', statusColors[roadmap.status])}>
                  {statusLabels[roadmap.status]}
                </span>
              </div>

              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {roadmap.title}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mb-4">{roadmap.description}</p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    시작일
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {format(startDate, 'yyyy.MM.dd', { locale: ko })}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    종료일
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {format(endDate, 'yyyy.MM.dd', { locale: ko })}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    기간
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {roadmap.duration_months}개월
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    남은 일수
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {daysRemaining}일
                  </div>
                </div>
              </div>

              {/* Time Progress */}
              <div className="mt-4">
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                  <span>진행 기간</span>
                  <span>{elapsedDays}/{totalDays}일</span>
                </div>
                <Progress
                  value={elapsedDays}
                  max={totalDays}
                  size="sm"
                  color="warning"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Finalize Warning Banner */}
      {roadmap.is_finalized && isEditMode && (
        <div className="bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/30 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-yellow-800 dark:text-yellow-300">
              확정된 로드맵 수정 중
            </h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
              이 로드맵은 확정되었습니다. 수정 시 변경 횟수가 기록됩니다.
              {roadmap.edit_count_after_finalize && roadmap.edit_count_after_finalize > 0 && (
                <span className="ml-1">
                  (현재 {roadmap.edit_count_after_finalize}회 수정됨)
                </span>
              )}
            </p>
          </div>
        </div>
      )}

      {/* Monthly Goals Drilldown */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">학습 계획</h2>
          <div className="flex items-center gap-2">
            {/* Edit Mode Toggle */}
            <Button
              variant={isEditMode ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setIsEditMode(!isEditMode)}
            >
              <Edit3 className="h-4 w-4 mr-1" />
              {isEditMode ? '편집 종료' : '편집'}
            </Button>

            {/* Finalize Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleFinalize}
              disabled={finalizeRoadmap.isPending || unfinalizeRoadmap.isPending}
            >
              {roadmap.is_finalized ? (
                <>
                  <Unlock className="h-4 w-4 mr-1" />
                  확정 해제
                </>
              ) : (
                <>
                  <Lock className="h-4 w-4 mr-1" />
                  확정
                </>
              )}
            </Button>
          </div>
        </div>

        <DrilldownContainer
          roadmap={roadmap}
          onToggleDailyTask={handleToggleDailyTask}
          isEditable={isEditMode}
          onEditDailyTask={handleEditDailyTask}
          onEditWeeklyTask={handleEditWeeklyTask}
          onEditMonthlyGoal={handleEditMonthlyGoal}
        />
      </div>

      {/* Edit Modals */}
      {editingDaily && (
        <EditTaskModal
          isOpen={true}
          onClose={() => setEditingDaily(null)}
          type="daily"
          title={editingDaily.task.title}
          description={editingDaily.task.description || ''}
          dayNumber={editingDaily.task.day_number}
          onSave={handleSaveDailyTask}
          onDelete={handleDeleteDailyTask}
          isLoading={updateDailyTask.isPending || deleteDailyTask.isPending}
          showFinalizeWarning={roadmap.is_finalized}
        />
      )}

      {editingWeekly && (
        <EditTaskModal
          isOpen={true}
          onClose={() => setEditingWeekly(null)}
          type="weekly"
          title={editingWeekly.task.title}
          description={editingWeekly.task.description || ''}
          onSave={handleSaveWeeklyTask}
          onDelete={handleDeleteWeeklyTask}
          isLoading={updateWeeklyTask.isPending || deleteWeeklyTask.isPending}
          showFinalizeWarning={roadmap.is_finalized}
        />
      )}

      {editingMonthly && (
        <EditTaskModal
          isOpen={true}
          onClose={() => setEditingMonthly(null)}
          type="monthly"
          title={editingMonthly.title}
          description={editingMonthly.description || ''}
          onSave={handleSaveMonthlyGoal}
          onDelete={handleDeleteMonthlyGoal}
          isLoading={updateMonthlyGoal.isPending || deleteMonthlyGoal.isPending}
          showFinalizeWarning={roadmap.is_finalized}
        />
      )}
    </div>
  );
}
