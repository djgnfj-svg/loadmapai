/**
 * 실시간 로드맵 생성 프리뷰 컴포넌트
 *
 * SSE 스트리밍으로 생성되는 로드맵을 실시간으로 표시합니다.
 * Framer Motion을 사용하여 부드러운 애니메이션 효과를 적용합니다.
 */
import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, CheckCircle2, Calendar, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { MonthPreview } from '@/hooks/useStreamingGeneration';

interface ProgressData {
  current_step: number;
  total_steps: number;
  percentage: number;
  message: string;
}

interface StreamingPreviewProps {
  title: string | null;
  description: string | null;
  months: MonthPreview[];
  progress: ProgressData | null;
  isComplete: boolean;
  isStreaming: boolean;
}

export function StreamingPreview({
  title,
  description,
  months,
  progress,
  isComplete,
  isStreaming,
}: StreamingPreviewProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // 새 콘텐츠가 추가되면 자동 스크롤
  useEffect(() => {
    if (scrollRef.current && months.length > 0) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [months]);

  return (
    <div className="space-y-6">
      {/* 진행률 */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-2">
            {isStreaming && <Loader2 className="h-4 w-4 animate-spin" />}
            {progress?.message || '준비 중...'}
          </span>
          <span className="font-medium">{progress?.percentage || 0}%</span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary-500 to-indigo-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress?.percentage || 0}%` }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* 제목 영역 */}
      <AnimatePresence>
        {title && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-gradient-to-r from-primary-50 to-indigo-50 dark:from-primary-500/10 dark:to-indigo-500/10 border border-primary-200 dark:border-primary-500/30 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-primary-500" />
              <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                로드맵 제목
              </span>
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {title}
            </h2>
            {description && (
              <p className="mt-2 text-gray-600 dark:text-gray-300">
                {description}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 월별 카드들 */}
      <div
        ref={scrollRef}
        className="space-y-4 max-h-[50vh] overflow-y-auto pr-2"
      >
        <AnimatePresence>
          {months.map((month, index) => (
            <motion.div
              key={month.month_number}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <MonthCard
                month={month}
                isGenerating={
                  index === months.length - 1 && isStreaming && !isComplete
                }
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 완료 메시지 */}
      <AnimatePresence>
        {isComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="text-center p-6 bg-green-50 dark:bg-green-500/10 border border-green-200 dark:border-green-500/30 rounded-xl"
          >
            <CheckCircle2 className="h-10 w-10 text-green-500 mx-auto mb-3" />
            <p className="font-semibold text-green-700 dark:text-green-400 text-lg">
              로드맵 생성이 완료되었습니다!
            </p>
            <p className="text-sm text-green-600 dark:text-green-500 mt-1">
              아래에서 검토 후 수정하거나 바로 시작할 수 있습니다.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * 월별 카드 컴포넌트
 */
function MonthCard({
  month,
  isGenerating,
}: {
  month: MonthPreview;
  isGenerating: boolean;
}) {
  const hasWeeks = month.weeks.length > 0;

  return (
    <div
      className={cn(
        'bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-xl overflow-hidden shadow-sm',
        isGenerating && !hasWeeks && 'animate-pulse'
      )}
    >
      {/* 상단 그라데이션 바 */}
      <div className="h-1 bg-gradient-to-r from-primary-500 to-indigo-500" />

      <div className="p-4">
        {/* 월 헤더 */}
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400">
            <Calendar className="h-3 w-3" />
            {month.month_number}월차
          </span>
          {isGenerating && !hasWeeks && (
            <span className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
              <Loader2 className="h-3 w-3 animate-spin" />
              주간 과제 생성 중...
            </span>
          )}
        </div>

        {/* 월 제목 및 설명 */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {month.title}
        </h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {month.description}
        </p>

        {/* 주간 과제들 */}
        {hasWeeks && (
          <div className="mt-4 space-y-2">
            <AnimatePresence>
              {month.weeks.map((week) => (
                <motion.div
                  key={week.week_number}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  className="pl-4 border-l-2 border-primary-200 dark:border-primary-500/30"
                >
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {week.week_number}주차: {week.title}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {week.description}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* 주간 생성 중 플레이스홀더 */}
        {isGenerating && !hasWeeks && (
          <div className="mt-4 space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="pl-4 border-l-2 border-gray-200 dark:border-dark-600"
              >
                <div className="h-4 bg-gray-200 dark:bg-dark-600 rounded w-48 animate-pulse" />
                <div className="h-3 bg-gray-100 dark:bg-dark-700 rounded w-64 mt-1 animate-pulse" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default StreamingPreview;
