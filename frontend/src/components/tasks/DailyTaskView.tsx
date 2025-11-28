import { useState } from 'react';
import { CheckCircle2, Circle, BookOpen, Play } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DailyTask } from '@/types';

interface DailyTaskViewProps {
  task: DailyTask;
  mode: 'planning' | 'learning';
  onToggle: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
}

export function DailyTaskView({ task, mode, onToggle, onStartQuiz }: DailyTaskViewProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg transition-colors',
        task.is_checked ? 'bg-green-50 dark:bg-green-500/10' : 'bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Checkbox */}
      <button
        onClick={() => onToggle(task.id)}
        className="flex-shrink-0"
      >
        {task.is_checked ? (
          <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
        ) : (
          <Circle className={cn(
            'h-5 w-5 transition-colors',
            isHovered ? 'text-primary-500' : 'text-gray-300 dark:text-gray-600'
          )} />
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
            Day {task.day_number}
          </span>
        </div>
        <p className={cn(
          'text-sm font-medium truncate',
          task.is_checked ? 'text-gray-500 dark:text-gray-400 line-through' : 'text-gray-900 dark:text-white'
        )}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
            {task.description}
          </p>
        )}
      </div>

      {/* Actions for Learning Mode */}
      {mode === 'learning' && (
        <button
          onClick={() => onStartQuiz?.(task.id)}
          className={cn(
            'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors',
            task.is_checked
              ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
              : 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400 hover:bg-primary-200 dark:hover:bg-primary-500/30'
          )}
        >
          {task.is_checked ? (
            <>
              <CheckCircle2 className="h-3 w-3" />
              완료
            </>
          ) : (
            <>
              <Play className="h-3 w-3" />
              퀴즈
            </>
          )}
        </button>
      )}
    </div>
  );
}
