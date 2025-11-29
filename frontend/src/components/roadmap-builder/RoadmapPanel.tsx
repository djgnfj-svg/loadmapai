import { cn } from '../../lib/utils';
import { RoadmapItem } from './RoadmapItem';
import type { ProgressiveRoadmap, ProgressiveDailyTask } from '../../types';
import type { DraftRoadmap } from '../../hooks/useProgressiveRoadmap';
import { ChevronDown, ChevronRight, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

interface RoadmapPanelProps {
  roadmap: ProgressiveRoadmap | null;
  isStreaming: boolean;
  progress: number;
  // NEW: 실시간 로드맵 초안
  draftRoadmap?: DraftRoadmap | null;
  className?: string;
}

export function RoadmapPanel({
  roadmap,
  isStreaming,
  progress,
  draftRoadmap,
  className,
}: RoadmapPanelProps) {
  // 완성도 (draftRoadmap에서 가져오거나 기본값)
  const completionPercentage = draftRoadmap?.completion_percentage || 0;

  if (!roadmap && !draftRoadmap) {
    return (
      <div className={cn('flex items-center justify-center h-full', className)}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-gray-400" />
          </div>
          <p className="font-medium">로드맵 미리보기</p>
          <p className="text-sm mt-1">질문에 답하시면 로드맵이 구체화됩니다</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 헤더 */}
      <div className="mb-4">
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

        {/* 완성도 진행률 */}
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2.5 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <span className={cn(
            'text-sm font-bold min-w-[3rem] text-right transition-colors duration-300',
            completionPercentage >= 80 ? 'text-green-600 dark:text-green-400' :
            completionPercentage >= 50 ? 'text-blue-600 dark:text-blue-400' :
            'text-gray-600 dark:text-gray-400'
          )}>
            {completionPercentage}%
          </span>
        </div>
      </div>

      {/* 로드맵 초안 뷰 (draftRoadmap이 있을 때) */}
      {draftRoadmap && draftRoadmap.months && draftRoadmap.months.length > 0 && (
        <DraftRoadmapView draftRoadmap={draftRoadmap} />
      )}

      {/* 전체 로드맵 뷰 (roadmap이 있을 때) */}
      {roadmap && (
        <div className="flex-1 overflow-y-auto">
          {/* 로드맵 제목/설명 */}
          <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
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
              <span>📚 {roadmap.topic}</span>
              <span>📅 {roadmap.duration_months}개월</span>
            </div>
          </div>

          {/* 월별 계획 */}
          <div className="space-y-3">
            {roadmap.monthly_goals.map((month) => (
              <MonthlyGoalCard key={month.month_number} month={month} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// 로드맵 초안 뷰 (간단한 월별 개요)
function DraftRoadmapView({ draftRoadmap }: { draftRoadmap: DraftRoadmap }) {
  return (
    <div className="mb-4 space-y-2">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-yellow-500" />
        AI가 구성 중인 로드맵 초안
      </div>
      <div className="space-y-2">
        {draftRoadmap.months.map((month, index) => (
          <DraftMonthCard key={month.month} month={month} index={index} />
        ))}
      </div>
    </div>
  );
}

// 초안 월 카드 (애니메이션 포함)
function DraftMonthCard({
  month,
  index
}: {
  month: DraftRoadmap['months'][0];
  index: number;
}) {
  const [isNew, setIsNew] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsNew(false), 1000);
    return () => clearTimeout(timer);
  }, [month.title, month.overview]);

  const isUndefined = month.title === '???' || !month.title;

  return (
    <div
      className={cn(
        'p-3 rounded-lg border transition-all duration-500',
        isNew && !isUndefined
          ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700 animate-pulse'
          : isUndefined
          ? 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-60'
          : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
      )}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex items-center gap-2">
        <span className={cn(
          'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
          isUndefined
            ? 'bg-gray-200 dark:bg-gray-700 text-gray-500'
            : 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400'
        )}>
          {month.month}
        </span>
        <span className={cn(
          'font-medium text-sm flex-1',
          isUndefined ? 'text-gray-400 italic' : 'text-gray-900 dark:text-white'
        )}>
          {month.title || '???'}
        </span>
        {isNew && !isUndefined && (
          <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full animate-bounce">
            NEW
          </span>
        )}
      </div>
      {month.overview && month.overview !== '???' && (
        <p className="mt-1 ml-8 text-xs text-gray-600 dark:text-gray-400">
          {month.overview}
        </p>
      )}
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
        <div className="mt-2 ml-5 space-y-2">
          {week.daily_tasks.map((day) => (
            <DailyTaskCard key={day.day_number} day={day} />
          ))}
        </div>
      )}
    </div>
  );
}

// Day별 다중 Task 지원 카드
function DailyTaskCard({ day }: { day: ProgressiveDailyTask }) {
  // tasks 배열이 있으면 사용, 없으면 legacy title/description 사용
  const tasks = day.tasks && day.tasks.length > 0
    ? day.tasks
    : day.title
      ? [{ title: day.title, description: day.description }]
      : [];

  if (tasks.length === 0) return null;

  return (
    <div className="border-l-2 border-blue-200 dark:border-blue-800 pl-2">
      {/* Day 헤더 */}
      <div className="flex items-center gap-2 mb-1">
        <span className="w-6 h-6 flex items-center justify-center rounded-md bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 text-[10px] font-bold">
          D{day.day_number}
        </span>
        <span className="text-[10px] text-gray-500 dark:text-gray-500">
          {tasks.length}개 Task
        </span>
      </div>

      {/* Tasks 목록 */}
      <div className="ml-2 space-y-1">
        {tasks.map((task, taskIndex) => (
          <div
            key={taskIndex}
            className={cn(
              'flex items-start gap-2 p-1.5 rounded text-xs transition-all',
              task.title.isNew
                ? 'bg-green-50 dark:bg-green-900/20 animate-pulse'
                : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
            )}
          >
            <span className="w-4 h-4 mt-0.5 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 text-[8px] text-gray-500 shrink-0">
              {taskIndex + 1}
            </span>
            <div className="flex-1 min-w-0">
              <RoadmapItem
                item={task.title}
                className="font-medium"
              />
              {task.description && task.description.content !== '???' && (
                <RoadmapItem
                  item={task.description}
                  className="text-gray-500 dark:text-gray-400 text-[10px] mt-0.5"
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
