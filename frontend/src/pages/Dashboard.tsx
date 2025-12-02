import { memo } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Map, Plus, ArrowRight } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useRoadmaps } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Progress, CircularProgress } from '@/components/common/Progress';
import { CardSkeleton } from '@/components/common/Loading';
import { STATUS_COLORS, STATUS_LABELS } from '@/constants';
import { cn } from '@/lib/utils';
import type { Roadmap } from '@/types';

const TodayTasks = memo(function TodayTasks({ roadmaps }: { roadmaps: Roadmap[] }) {
  const totalProgress = roadmaps.length > 0
    ? Math.round(roadmaps.reduce((sum, r) => sum + (r.progress || 0), 0) / roadmaps.length)
    : 0;

  const activeRoadmaps = roadmaps.filter(r => r.status.toUpperCase() === 'ACTIVE');

  return (
    <Card variant="bordered" className="h-full">
      <CardHeader>
        <CardTitle>오늘의 학습</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-6 mb-6">
          <CircularProgress value={totalProgress} size={100} />
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">전체 진행률</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalProgress}%</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{activeRoadmaps.length}개 로드맵 진행 중</p>
          </div>
        </div>

        {activeRoadmaps.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-gray-500 dark:text-gray-400 mb-4">진행 중인 로드맵이 없습니다.</p>
            <Link to="/roadmaps/create">
              <Button variant="primary" size="sm">
                <Plus className="h-4 w-4 mr-1" />
                새 로드맵 만들기
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {activeRoadmaps.slice(0, 3).map((roadmap) => (
              <Link
                key={roadmap.id}
                to={`/roadmaps/${roadmap.id}`}
                className={cn(
                  'block p-3 rounded-xl transition-colors',
                  'bg-gray-50 dark:bg-dark-700',
                  'hover:bg-gray-100 dark:hover:bg-dark-600'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-white truncate">
                    {roadmap.title}
                  </span>
                </div>
                <Progress value={roadmap.progress || 0} size="sm" />
              </Link>
            ))}
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
              <Map className="h-5 w-5 text-primary-600 dark:text-primary-400" />
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
}

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
        <Map className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
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
          <TodayTasks roadmaps={roadmaps || []} />
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
                    <Map className="h-6 w-6 text-green-600 dark:text-green-400" />
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
