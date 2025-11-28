import { Sparkles } from 'lucide-react';
import { StreamingProgress } from '@/components/common/StreamingProgress';
import type { StreamEvent } from '@/hooks/useStreaming';

interface StreamingGeneratingStateProps {
  topic: string;
  events: StreamEvent[];
  currentEvent: StreamEvent | null;
  progress: number;
  isStreaming: boolean;
  error: string | null;
}

export function StreamingGeneratingState({
  topic,
  events,
  currentEvent,
  progress,
  isStreaming,
  error,
}: StreamingGeneratingStateProps) {
  return (
    <div className="py-8 space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="relative inline-flex mb-4">
          <div className="p-4 rounded-full bg-primary-100 dark:bg-primary-500/20">
            <Sparkles className="h-8 w-8 text-primary-600 dark:text-primary-400 animate-pulse" />
          </div>
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          AI가 맞춤형 로드맵을 생성 중입니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400">
          "{topic}"에 대한 개인 맞춤형 학습 계획을 만들고 있어요
        </p>
      </div>

      {/* Streaming Progress */}
      <div className="max-w-md mx-auto">
        <StreamingProgress
          events={events}
          currentEvent={currentEvent}
          progress={progress}
          isStreaming={isStreaming}
          error={error}
        />
      </div>

      {/* Helpful tips while waiting */}
      {isStreaming && progress < 50 && (
        <div className="text-center text-sm text-gray-400 dark:text-gray-500 space-y-1">
          <p>AI가 최적의 학습 경로를 분석하고 있습니다</p>
        </div>
      )}
      {isStreaming && progress >= 50 && progress < 80 && (
        <div className="text-center text-sm text-gray-400 dark:text-gray-500 space-y-1">
          <p>학습 계획을 세부적으로 구성하고 있습니다</p>
        </div>
      )}
      {isStreaming && progress >= 80 && (
        <div className="text-center text-sm text-gray-400 dark:text-gray-500 space-y-1">
          <p>거의 완료되었습니다!</p>
        </div>
      )}
    </div>
  );
}
