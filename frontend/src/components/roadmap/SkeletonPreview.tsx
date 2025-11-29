import { Calendar, ChevronRight, Loader2, MapPin } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RoadmapSkeleton, SkeletonMonth } from '@/types';

interface SkeletonPreviewProps {
  skeleton: RoadmapSkeleton | null;
  isLoading: boolean;
  error?: string | null;
  topic: string;
  className?: string;
}

export function SkeletonPreview({
  skeleton,
  isLoading,
  error,
  topic,
  className,
}: SkeletonPreviewProps) {
  if (error) {
    return (
      <div className={cn('p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400', className)}>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (isLoading && !skeleton) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>로드맵 구조 생성 중...</span>
        </div>
        <SkeletonPlaceholder count={3} />
      </div>
    );
  }

  if (!skeleton) {
    return (
      <div className={cn('p-6 rounded-lg bg-gray-50 dark:bg-dark-700 text-center', className)}>
        <MapPin className="h-8 w-8 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          로드맵 구조가 여기에 표시됩니다
        </p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex items-center gap-2 pb-2 border-b border-gray-200 dark:border-dark-600">
        <MapPin className="h-5 w-5 text-primary-500" />
        <h3 className="font-semibold text-gray-900 dark:text-white">
          {topic} 로드맵
        </h3>
      </div>

      {/* Months */}
      <div className="space-y-2">
        {skeleton.months.map((month) => (
          <MonthSkeletonCard
            key={month.month_number}
            month={month}
          />
        ))}
      </div>
    </div>
  );
}

interface MonthSkeletonCardProps {
  month: SkeletonMonth;
}

function MonthSkeletonCard({ month }: MonthSkeletonCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border overflow-hidden transition-all',
        'border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800'
      )}
    >
      {/* Month Header */}
      <div className="px-3 py-2.5 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-500/10 dark:to-transparent">
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 dark:bg-primary-500/20">
            <Calendar className="h-3.5 w-3.5 text-primary-600 dark:text-primary-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              {month.month_number}월: {month.title}
            </h4>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {month.description}
            </p>
          </div>
        </div>
      </div>

      {/* Weeks */}
      <div className="divide-y divide-gray-100 dark:divide-dark-600">
        {month.weeks.map((week) => (
          <div
            key={week.week_number}
            className="px-3 py-1.5 flex items-center gap-2 text-sm"
          >
            <ChevronRight className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
            <span className="text-gray-600 dark:text-gray-400">
              {week.week_number}주차:
            </span>
            <span className="text-gray-800 dark:text-gray-200 truncate">
              {week.title}
            </span>
            {/* Empty slot indicator */}
            <div className="ml-auto flex gap-1">
              {[1, 2, 3, 4, 5].map((day) => (
                <div
                  key={day}
                  className="w-2 h-2 rounded-sm bg-gray-200 dark:bg-dark-500"
                  title={`${day}일차 (대기 중)`}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SkeletonPlaceholder({ count }: { count: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="rounded-lg border border-gray-200 dark:border-dark-600 overflow-hidden animate-pulse"
        >
          <div className="px-3 py-2.5 bg-gray-100 dark:bg-dark-700">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-gray-200 dark:bg-dark-500" />
              <div className="flex-1">
                <div className="h-4 w-24 bg-gray-200 dark:bg-dark-500 rounded" />
                <div className="h-3 w-32 bg-gray-200 dark:bg-dark-500 rounded mt-1" />
              </div>
            </div>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-dark-600">
            {[1, 2, 3, 4].map((week) => (
              <div key={week} className="px-3 py-1.5 flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-gray-200 dark:bg-dark-500" />
                <div className="h-3 w-20 bg-gray-200 dark:bg-dark-500 rounded" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
