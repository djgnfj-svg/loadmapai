import { memo, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Map as MapIcon, Plus, ArrowRight, CheckCircle2, Circle, Target } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useRoadmaps, useUnifiedToday, useToggleDailyTaskUnified } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Progress } from '@/components/common/Progress';
import { CardSkeleton } from '@/components/common/Loading';
import { STATUS_COLORS, STATUS_LABELS } from '@/constants';
import { cn } from '@/lib/utils';
import type { Roadmap } from '@/types';

// 로드맵별 색상
const ROADMAP_COLORS = [
  { bg: 'bg-blue-100 dark:bg-blue-500/20', text: 'text-blue-700 dark:text-blue-400', accent: 'bg-blue-500' },
  { bg: 'bg-purple-100 dark:bg-purple-500/20', text: 'text-purple-700 dark:text-purple-400', accent: 'bg-purple-500' },
  { bg: 'bg-green-100 dark:bg-green-500/20', text: 'text-green-700 dark:text-green-400', accent: 'bg-green-500' },
  { bg: 'bg-orange-100 dark:bg-orange-500/20', text: 'text-orange-700 dark:text-orange-400', accent: 'bg-orange-500' },
];

function getRoadmapColor(index: number) {
  return ROADMAP_COLORS[index % ROADMAP_COLORS.length];
}

const TodayTasks = memo(function TodayTasks() {
  const { data, isLoading } = useUnifiedToday();
  const toggleMutation = useToggleDailyTaskUnified();

  // 로드맵별 색상 매핑
  const colorMap = useMemo(() => {
    if (!data) return new Map<string, number>();
    const uniqueIds = [...new Set(data.today_tasks.map(t => t.roadmap_id))];
    const map = new Map<string, number>();
    uniqueIds.forEach((id, index) => map.set(id, index));
    return map;
  }, [data]);

  const handleToggle = (taskId: string) => {
    toggleMutation.mutate(taskId);
  };

  if (isLoading) {
    return (
      <Card variant="bordered" className="h-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary-500" />
            오늘 할 일
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-14 bg-gray-100 dark:bg-dark-700 rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const todayTasks = data?.today_tasks || [];
  const completed = data?.today_completed || 0;
  const total = data?.today_total || 0;

  return (
    <Card variant="bordered" className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-primary-500" />
          오늘 할 일
        </CardTitle>
        {total > 0 && (
          <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
            {completed}/{total}
          </span>
        )}
      </CardHeader>
      <CardContent>
        {todayTasks.length === 0 ? (
          <div className="text-center py-6">
            <CheckCircle2 className="h-10 w-10 mx-auto text-green-500 mb-3" />
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              오늘 예정된 학습이 없습니다
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {todayTasks.map((task) => {
              const color = getRoadmapColor(colorMap.get(task.roadmap_id) || 0);
              return (
                <div
                  key={task.id}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg transition-all',
                    task.is_checked
                      ? 'bg-green-50 dark:bg-green-500/10'
                      : 'bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600'
                  )}
                >
                  <div className={cn('w-1 h-10 rounded-full flex-shrink-0', color.accent)} />
                  <button
                    onClick={() => handleToggle(task.id)}
                    disabled={toggleMutation.isPending}
                    className="flex-shrink-0"
                  >
                    {task.is_checked ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    ) : (
                      <Circle className="h-5 w-5 text-gray-300 dark:text-gray-600 hover:text-primary-500" />
                    )}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className={cn(
                      'text-sm font-medium truncate',
                      task.is_checked
                        ? 'text-gray-400 dark:text-gray-500 line-through'
                        : 'text-gray-900 dark:text-white'
                    )}>
                      {task.title}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={cn('text-xs px-1.5 py-0.5 rounded', color.bg, color.text)}>
                        {task.roadmap_title}
                      </span>
                      <span className="text-xs text-gray-400 dark:text-gray-500 truncate">
                        {task.weekly_task_title}
                      </span>
                    </div>
                  </div>
                  <Link
                    to={`/roadmaps/${task.roadmap_id}`}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-primary-500"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
});

const RoadmapCard = memo(function RoadmapCard({ roadmap }: { roadmap: Roadmap }) {
  const statusKey = roadmap.status.toUpperCase() as keyof typeof STATUS_COLORS;

  return (
    <Link to={`/roadmaps/${roadmap.id}`}>
      <Card variant="bordered" hover className="h-full">
        <CardContent>
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <MapIcon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <span className={cn('px-2 py-0.5 text-xs rounded-full', STATUS_COLORS[statusKey])}>
                {STATUS_LABELS[statusKey]}
              </span>
            </div>
          </div>

          <h3 className="font-semibold text-gray-900 dark:text-white mb-1 line-clamp-1">
            {roadmap.title}
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-4">
            {roadmap.description}
          </p>

          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
              <span>진행률</span>
              <span>{roadmap.progress || 0}%</span>
            </div>
            <Progress value={roadmap.progress || 0} size="sm" />
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>{roadmap.duration_months}개월 과정</span>
            <span>
              {format(new Date(roadmap.start_date), 'yyyy.MM.dd', { locale: ko })} ~
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
});

function RecentRoadmaps({ roadmaps, isLoading }: { roadmaps: Roadmap[]; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (roadmaps.length === 0) {
    return (
      <Card variant="bordered" className="text-center py-12">
        <MapIcon className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          아직 로드맵이 없습니다
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          AI가 당신만의 학습 로드맵을 만들어 드립니다.
        </p>
        <Link to="/roadmaps/create">
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-1" />
            첫 로드맵 만들기
          </Button>
        </Link>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {roadmaps.slice(0, 6).map((roadmap) => (
        <RoadmapCard key={roadmap.id} roadmap={roadmap} />
      ))}
    </div>
  );
}

export function Dashboard() {
  const { user } = useAuthStore();
  const { data: roadmaps, isLoading } = useRoadmaps();

  const today = format(new Date(), 'yyyy년 M월 d일 EEEE', { locale: ko });

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            안녕하세요, {user?.name}님!
          </h1>
          <p className="text-gray-500 dark:text-gray-400">{today}</p>
        </div>
        <Link to="/roadmaps/create" className="shrink-0">
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-1" />
            새 로드맵
          </Button>
        </Link>
      </div>

      {/* Today's Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <TodayTasks />
        </div>
        <div className="lg:col-span-2">
          <Card variant="bordered" className="h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>빠른 시작</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                  to="/roadmaps/create"
                  className={cn(
                    'flex items-center gap-4 p-4 rounded-xl',
                    'border border-gray-200 dark:border-dark-600',
                    'hover:border-primary-300 dark:hover:border-primary-500',
                    'hover:bg-primary-50 dark:hover:bg-primary-500/10',
                    'transition-colors'
                  )}
                >
                  <div className="p-3 rounded-full bg-primary-100 dark:bg-primary-500/20">
                    <Plus className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">새 로드맵 생성</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">AI로 학습 계획 만들기</p>
                  </div>
                </Link>
                <Link
                  to="/roadmaps"
                  className={cn(
                    'flex items-center gap-4 p-4 rounded-xl',
                    'border border-gray-200 dark:border-dark-600',
                    'hover:border-primary-300 dark:hover:border-primary-500',
                    'hover:bg-primary-50 dark:hover:bg-primary-500/10',
                    'transition-colors'
                  )}
                >
                  <div className="p-3 rounded-full bg-green-100 dark:bg-green-500/20">
                    <MapIcon className="h-6 w-6 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">내 로드맵</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">진행 중인 로드맵 보기</p>
                  </div>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recent Roadmaps */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">최근 로드맵</h2>
          {(roadmaps?.length ?? 0) > 0 && (
            <Link
              to="/roadmaps"
              className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center gap-1"
            >
              전체 보기
              <ArrowRight className="h-4 w-4" />
            </Link>
          )}
        </div>
        <RecentRoadmaps roadmaps={roadmaps || []} isLoading={isLoading} />
      </div>
    </div>
  );
}
