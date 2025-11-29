import { cn } from '../../lib/utils';
import { RoadmapItem } from './RoadmapItem';
import type { ProgressiveRoadmap } from '../../types';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface RoadmapPanelProps {
  roadmap: ProgressiveRoadmap | null;
  isStreaming: boolean;
  progress: number;
  className?: string;
}

export function RoadmapPanel({
  roadmap,
  isStreaming,
  progress,
  className,
}: RoadmapPanelProps) {
  if (!roadmap) {
    return (
      <div className={cn('flex items-center justify-center h-full', className)}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p>로드맵을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 헤더 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            로드맵 미리보기
          </h2>
          {isStreaming && (
            <div className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
              <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              구체화 중...
            </div>
          )}
        </div>

        {/* 진행률 */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
          <div
            className="bg-green-500 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 로드맵 제목/설명 */}
      <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <RoadmapItem
          item={roadmap.title}
          as="h3"
          className="text-lg font-bold mb-2"
        />
        <RoadmapItem
          item={roadmap.description}
          as="p"
          className="text-sm"
        />
        <div className="mt-2 flex gap-4 text-xs text-gray-500 dark:text-gray-400">
          <span>주제: {roadmap.topic}</span>
          <span>기간: {roadmap.duration_months}개월</span>
        </div>
      </div>

      {/* 월별 계획 */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {roadmap.monthly_goals.map((month) => (
          <MonthlyGoalCard key={month.month_number} month={month} />
        ))}
      </div>
    </div>
  );
}

interface MonthlyGoalCardProps {
  month: ProgressiveRoadmap['monthly_goals'][0];
}

function MonthlyGoalCard({ month }: MonthlyGoalCardProps) {
  const [isExpanded, setIsExpanded] = useState(month.month_number === 1);

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      {/* 월 헤더 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-500" />
        )}
        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
          {month.month_number}월
        </span>
        <RoadmapItem
          item={month.title}
          className="text-sm font-medium flex-1 text-left"
        />
      </button>

      {/* 주간 목록 */}
      {isExpanded && (
        <div className="p-3 space-y-2">
          <RoadmapItem
            item={month.description}
            as="p"
            className="text-xs text-gray-600 dark:text-gray-400 mb-3"
          />

          {month.weekly_tasks.map((week) => (
            <WeeklyTaskCard key={week.week_number} week={week} />
          ))}
        </div>
      )}
    </div>
  );
}

interface WeeklyTaskCardProps {
  week: ProgressiveRoadmap['monthly_goals'][0]['weekly_tasks'][0];
}

function WeeklyTaskCard({ week }: WeeklyTaskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="ml-4 border-l-2 border-gray-200 dark:border-gray-600 pl-3">
      {/* 주 헤더 */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 text-left hover:bg-gray-50 dark:hover:bg-gray-800 rounded p-1 -ml-1"
      >
        {isExpanded ? (
          <ChevronDown className="w-3 h-3 text-gray-400" />
        ) : (
          <ChevronRight className="w-3 h-3 text-gray-400" />
        )}
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
          {week.week_number}주차
        </span>
        <RoadmapItem
          item={week.title}
          className="text-xs flex-1"
        />
      </button>

      {/* 일간 목록 */}
      {isExpanded && (
        <div className="mt-2 ml-5 space-y-1">
          {week.daily_tasks.map((day) => (
            <div
              key={day.day_number}
              className="flex items-center gap-2 text-xs"
            >
              <span className="w-5 h-5 flex items-center justify-center rounded bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-[10px]">
                D{day.day_number}
              </span>
              <RoadmapItem item={day.title} className="flex-1" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
