import { useState } from 'react';
import { cn } from '../../lib/utils';
import { QuestionPanel } from './QuestionPanel';
import { RoadmapPanel } from './RoadmapPanel';
import type { InterviewQuestion, ProgressiveRoadmap } from '../../types';
import type { AIFeedback, DraftRoadmap } from '../../hooks/useProgressiveRoadmap';

interface SplitViewContainerProps {
  // 질문 관련
  questions: InterviewQuestion[];
  answers: Map<string, string>;
  onAnswerChange: (questionId: string, answer: string) => void;
  onSubmit: (userWantsComplete?: boolean) => Promise<void>;  // 변경: 완료 여부 파라미터
  isSubmitting: boolean;

  // 로드맵 관련
  roadmap: ProgressiveRoadmap | null;
  isStreaming: boolean;
  progress: number;

  // 다중 라운드 인터뷰 (NEW)
  currentRound?: number;
  maxRounds?: number;
  feedback?: AIFeedback | null;
  draftRoadmap?: DraftRoadmap | null;
  informationLevel?: 'insufficient' | 'minimal' | 'sufficient' | 'complete' | null;
  aiRecommendsComplete?: boolean;
  canComplete?: boolean;

  // 옵션
  className?: string;
}

type MobileTab = 'questions' | 'roadmap';

export function SplitViewContainer({
  questions,
  answers,
  onAnswerChange,
  onSubmit,
  isSubmitting,
  roadmap,
  isStreaming,
  progress,
  // 다중 라운드 인터뷰 props
  currentRound = 1,
  maxRounds = 10,
  feedback,
  draftRoadmap,
  informationLevel,
  aiRecommendsComplete = false,
  canComplete = false,
  className,
}: SplitViewContainerProps) {
  const [mobileTab, setMobileTab] = useState<MobileTab>('questions');

  return (
    <div className={cn('h-full', className)}>
      {/* 모바일: 탭 전환 */}
      <div className="lg:hidden mb-4">
        <div className="flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1">
          <button
            onClick={() => setMobileTab('questions')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              mobileTab === 'questions'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400'
            )}
          >
            질문 ({answers.size}/{questions.length})
          </button>
          <button
            onClick={() => setMobileTab('roadmap')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all',
              mobileTab === 'roadmap'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400'
            )}
          >
            로드맵
            {isStreaming && (
              <span className="ml-2 inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            )}
          </button>
        </div>
      </div>

      {/* 모바일: 선택된 탭 표시 */}
      <div className="lg:hidden h-[calc(100%-60px)]">
        {mobileTab === 'questions' ? (
          <QuestionPanel
            questions={questions}
            answers={answers}
            onAnswerChange={onAnswerChange}
            onSubmit={onSubmit}
            isSubmitting={isSubmitting}
            currentRound={currentRound}
            maxRounds={maxRounds}
            feedback={feedback}
            draftRoadmap={draftRoadmap}
            informationLevel={informationLevel}
            aiRecommendsComplete={aiRecommendsComplete}
            canComplete={canComplete}
            className="h-full"
          />
        ) : (
          <RoadmapPanel
            roadmap={roadmap}
            isStreaming={isStreaming}
            progress={progress}
            className="h-full"
          />
        )}
      </div>

      {/* 데스크톱: 2분할 뷰 */}
      <div className="hidden lg:grid lg:grid-cols-2 lg:gap-6 h-full">
        <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 overflow-hidden">
          <QuestionPanel
            questions={questions}
            answers={answers}
            onAnswerChange={onAnswerChange}
            onSubmit={onSubmit}
            isSubmitting={isSubmitting}
            currentRound={currentRound}
            maxRounds={maxRounds}
            feedback={feedback}
            draftRoadmap={draftRoadmap}
            informationLevel={informationLevel}
            aiRecommendsComplete={aiRecommendsComplete}
            canComplete={canComplete}
            className="h-full"
          />
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 overflow-hidden">
          <RoadmapPanel
            roadmap={roadmap}
            isStreaming={isStreaming}
            progress={progress}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}
