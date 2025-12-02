import { useState, useMemo, memo } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Map, Search, MoreVertical, Trash2, Pause, Play } from 'lucide-react';
import { useRoadmaps, useDeleteRoadmap } from '@/hooks';
import { roadmapApi } from '@/lib/api';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Progress } from '@/components/common/Progress';
import { CardSkeleton } from '@/components/common/Loading';
import { STATUS_COLORS, STATUS_LABELS } from '@/constants';
import type { Roadmap } from '@/types';

const RoadmapCard = memo(function RoadmapCard({
  roadmap,
  onDelete,
  onToggleStatus,
}: {
  roadmap: Roadmap;
  onDelete: (id: string) => void;
  onToggleStatus: (id: string, status: string) => void;
}) {
  const [showMenu, setShowMenu] = useState(false);
  const statusKey = roadmap.status.toUpperCase() as keyof typeof STATUS_COLORS;

  return (
    <Card variant="bordered" className="relative hover:shadow-md transition-shadow">
      <CardContent>
        {/* Menu Button */}
        <div className="absolute top-4 right-4">
          <button
            onClick={(e) => {
              e.preventDefault();
              setShowMenu(!showMenu);
            }}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-dark-600"
          >
            <MoreVertical className="h-5 w-5 text-gray-400 dark:text-gray-500" />
          </button>
          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 mt-1 w-36 bg-white dark:bg-dark-800 rounded-lg shadow-lg border border-gray-200 dark:border-dark-600 py-1 z-20">
                {roadmap.status === 'active' ? (
                  <button
                    onClick={() => {
                      onToggleStatus(roadmap.id, 'paused');
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
                      onToggleStatus(roadmap.id, 'active');
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
                    if (window.confirm('정말 삭제하시겠습니까?')) {
                      onDelete(roadmap.id);
                    }
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

        <Link to={`/roadmaps/${roadmap.id}`}>
          <div className="flex items-start gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-500/20">
              <Map className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`px-2 py-0.5 text-xs rounded-full ${STATUS_COLORS[statusKey]}`}>
                  {STATUS_LABELS[statusKey]}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white truncate pr-8">
                {roadmap.title}
              </h3>
            </div>
          </div>

          <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-4">
            {roadmap.description}
          </p>

          <div className="mb-4">
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
              <span>진행률</span>
              <span>{roadmap.progress || 0}%</span>
            </div>
            <Progress value={roadmap.progress || 0} size="sm" />
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>{roadmap.duration_months}개월 과정</span>
            <span>
              {format(new Date(roadmap.start_date), 'yyyy.MM.dd', { locale: ko })}
            </span>
          </div>
        </Link>
      </CardContent>
    </Card>
  );
}

export function RoadmapList() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'paused' | 'completed'>('all');

  const { data: roadmaps, isLoading } = useRoadmaps();
  const deleteRoadmap = useDeleteRoadmap();
  const queryClient = useQueryClient();

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      roadmapApi.update(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
    },
  });

  const filteredRoadmaps = useMemo(() => {
    return (roadmaps || []).filter((roadmap) => {
      const matchesSearch = roadmap.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        roadmap.topic.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filter === 'all' || roadmap.status.toUpperCase() === filter.toUpperCase();
      return matchesSearch && matchesFilter;
    });
  }, [roadmaps, searchQuery, filter]);

  const handleDelete = (id: string) => {
    deleteRoadmap.mutate(id);
  };

  const handleToggleStatus = (id: string, status: string) => {
    updateStatusMutation.mutate({ id, status });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">내 로드맵</h1>
          <p className="text-gray-500 dark:text-gray-400">총 {roadmaps?.length || 0}개의 로드맵</p>
        </div>
        <Link to="/roadmaps/create">
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-1" />
            새 로드맵
          </Button>
        </Link>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="로드맵 검색..."
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'active', 'paused', 'completed'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-2 text-sm rounded-lg transition-colors ${
                filter === f
                  ? 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400'
                  : 'bg-gray-100 dark:bg-dark-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-600'
              }`}
            >
              {f === 'all' ? '전체' : f === 'active' ? '진행 중' : f === 'paused' ? '일시정지' : '완료'}
            </button>
          ))}
        </div>
      </div>

      {/* Roadmap Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredRoadmaps.length === 0 ? (
        <Card variant="bordered" className="text-center py-12">
          <Map className="h-12 w-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {searchQuery || filter !== 'all'
              ? '검색 결과가 없습니다'
              : '아직 로드맵이 없습니다'}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            {searchQuery || filter !== 'all'
              ? '다른 검색어나 필터를 사용해 보세요.'
              : 'AI가 당신만의 학습 로드맵을 만들어 드립니다.'}
          </p>
          {!searchQuery && filter === 'all' && (
            <Link to="/roadmaps/create">
              <Button variant="primary">
                <Plus className="h-4 w-4 mr-1" />
                첫 로드맵 만들기
              </Button>
            </Link>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRoadmaps.map((roadmap) => (
            <RoadmapCard
              key={roadmap.id}
              roadmap={roadmap}
              onDelete={handleDelete}
              onToggleStatus={handleToggleStatus}
            />
          ))}
        </div>
      )}
    </div>
  );
}
