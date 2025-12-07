import { Card } from '@/components/common/Card';
import { cn } from '@/lib/utils';
import type { RoadmapMode } from '@/types';

interface ModeSelectionProps {
  selectedMode: RoadmapMode;
  onModeSelect: (mode: RoadmapMode) => void;
}

interface ModeOption {
  value: RoadmapMode;
  title: string;
  description: string;
  icon: React.ReactNode;
  features: string[];
}

const modeOptions: ModeOption[] = [
  {
    value: 'PLANNING',
    title: '계획 모드',
    description: '체크리스트 형태로 할 일을 관리합니다',
    icon: (
      <svg
        className="w-10 h-10"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
        />
      </svg>
    ),
    features: [
      '일일 태스크 체크리스트',
      '자유로운 진도 관리',
      '유연한 학습 스케줄',
    ],
  },
  {
    value: 'LEARNING',
    title: '학습 모드',
    description: '문제 풀이 형태로 학습 효과를 극대화합니다',
    icon: (
      <svg
        className="w-10 h-10"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
    ),
    features: [
      '서술형, 객관식, 단답식 문제',
      '즉각적인 AI 피드백',
      '틀린 문제 복습 시스템',
    ],
  },
];

export function ModeSelection({ selectedMode, onModeSelect }: ModeSelectionProps) {
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          어떤 방식으로 학습할까요?
        </h2>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          학습 스타일에 맞는 모드를 선택하세요
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modeOptions.map((option) => {
          const isSelected = selectedMode === option.value;

          return (
            <button
              key={option.value}
              onClick={() => onModeSelect(option.value)}
              className="text-left w-full"
            >
              <Card
                variant={isSelected ? 'elevated' : 'bordered'}
                hover
                className={cn(
                  'h-full transition-all duration-300',
                  isSelected && 'ring-2 ring-primary-500 border-primary-500'
                )}
              >
                <div className="p-6">
                  {/* Icon and Title */}
                  <div className="flex items-start gap-4 mb-4">
                    <div
                      className={cn(
                        'p-3 rounded-xl',
                        isSelected
                          ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'
                          : 'bg-gray-100 text-gray-600 dark:bg-dark-700 dark:text-gray-400'
                      )}
                    >
                      {option.icon}
                    </div>
                    <div className="flex-1">
                      <h3
                        className={cn(
                          'text-lg font-semibold',
                          isSelected
                            ? 'text-primary-600 dark:text-primary-400'
                            : 'text-gray-900 dark:text-white'
                        )}
                      >
                        {option.title}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {option.description}
                      </p>
                    </div>
                    {/* Selection Indicator */}
                    <div
                      className={cn(
                        'w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0',
                        isSelected
                          ? 'border-primary-500 bg-primary-500'
                          : 'border-gray-300 dark:border-dark-600'
                      )}
                    >
                      {isSelected && (
                        <svg
                          className="w-4 h-4 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-2 mt-4 pt-4 border-t border-gray-100 dark:border-dark-700">
                    {option.features.map((feature, index) => (
                      <li
                        key={index}
                        className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
                      >
                        <svg
                          className={cn(
                            'w-4 h-4 flex-shrink-0',
                            isSelected
                              ? 'text-primary-500'
                              : 'text-gray-400 dark:text-gray-500'
                          )}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            </button>
          );
        })}
      </div>
    </div>
  );
}
