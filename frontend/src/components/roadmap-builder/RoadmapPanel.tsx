import { cn } from '../../lib/utils';
import { Sparkles, CheckCircle, ArrowRight } from 'lucide-react';

interface RoadmapPanelProps {
  isReadyForGeneration: boolean;
  isStreaming: boolean;
  currentRound: number;
  progress?: number;
  className?: string;
}

export function RoadmapPanel({
  isReadyForGeneration,
  isStreaming,
  currentRound,
  progress = 0,
  className,
}: RoadmapPanelProps) {

  // 인터뷰 완료 - 로드맵 생성 준비됨
  if (isReadyForGeneration) {
    return (
      <div className={cn('flex flex-col items-center justify-center h-full p-8', className)}>
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            인터뷰 완료!
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            맞춤형 로드맵을 생성할 준비가 되었습니다.
          </p>
          <div className="flex items-center justify-center gap-2 text-sm text-green-600 dark:text-green-400">
            <ArrowRight className="w-4 h-4" />
            <span>아래 버튼을 눌러 로드맵을 생성하세요</span>
          </div>
        </div>
      </div>
    );
  }

  // 로드맵 생성 중 (스트리밍)
  if (isStreaming && progress > 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center h-full p-8', className)}>
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            로드맵 생성 중...
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            AI가 맞춤형 로드맵을 만들고 있습니다
          </p>

          {/* 진행률 바 */}
          <div className="w-64 mx-auto">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-green-500 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">{progress}%</p>
          </div>
        </div>
      </div>
    );
  }

  // 기본 상태 - 인터뷰 진행 중
  return (
    <div className={cn('flex flex-col items-center justify-center h-full p-8', className)}>
      <div className="text-center">
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <Sparkles className="w-10 h-10 text-primary-500 dark:text-primary-400" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          인터뷰 진행 중
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          모든 질문에 답변하면 맞춤형 로드맵이 생성됩니다
        </p>

        {/* 라운드 진행 표시 */}
        <div className="flex items-center justify-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-colors',
            currentRound >= 1 ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
          )}>
            1
          </div>
          <div className={cn(
            'w-8 h-0.5 transition-colors',
            currentRound >= 2 ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'
          )} />
          <div className={cn(
            'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-colors',
            currentRound >= 2 ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
          )}>
            2
          </div>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          {currentRound === 1 ? '기본 질문 단계' : 'AI 추가 질문 단계'}
        </p>
      </div>
    </div>
  );
}
