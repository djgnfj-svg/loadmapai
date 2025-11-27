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
        task.is_checked ? 'bg-green-50' : 'bg-gray-50 hover:bg-gray-100'
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
          <CheckCircle2 className="h-5 w-5 text-green-600" />
        ) : (
          <Circle className={cn(
            'h-5 w-5 transition-colors',
            isHovered ? 'text-primary-500' : 'text-gray-300'
          )} />
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500">
            Day {task.day_number}
          </span>
        </div>
        <p className={cn(
          'text-sm font-medium truncate',
          task.is_checked ? 'text-gray-500 line-through' : 'text-gray-900'
        )}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-gray-500 truncate mt-0.5">
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
              ? 'bg-green-100 text-green-700'
              : 'bg-primary-100 text-primary-700 hover:bg-primary-200'
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
