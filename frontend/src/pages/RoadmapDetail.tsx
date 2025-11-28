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
  BookOpen,
} from 'lucide-react';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRoadmapFull, useToggleDailyTask, useDeleteRoadmap } from '@/hooks';
import { roadmapApi } from '@/lib/api';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { CircularProgress, Progress } from '@/components/common/Progress';
import { LoadingScreen } from '@/components/common/Loading';
import { DrilldownContainer } from '@/components/tasks';
import { cn } from '@/lib/utils';

export function RoadmapDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);

  const { data: roadmap, isLoading, error } = useRoadmapFull(id || '');
  const toggleDailyTask = useToggleDailyTask();
  const deleteRoadmap = useDeleteRoadmap();
  const queryClient = useQueryClient();

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

  const handleStartQuiz = (taskId: string) => {
    navigate(`/quiz/${taskId}`);
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
                {/* Mode Badge - Prominent */}
                <span className={cn(
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold',
                  roadmap.mode === 'learning'
                    ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
                    : 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400'
                )}>
                  {roadmap.mode === 'learning' ? (
                    <>
                      <BookOpen className="h-4 w-4" />
                      러닝 모드
                    </>
                  ) : (
                    <>
                      <Map className="h-4 w-4" />
                      플래닝 모드
                    </>
                  )}
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

      {/* Monthly Goals Drilldown */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">학습 계획</h2>
        <DrilldownContainer
          roadmap={roadmap}
          onToggleDailyTask={handleToggleDailyTask}
          onStartQuiz={handleStartQuiz}
        />
      </div>
    </div>
  );
}
