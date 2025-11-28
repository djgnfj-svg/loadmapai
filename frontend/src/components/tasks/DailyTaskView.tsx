import { useState } from 'react';
import { CheckCircle2, Circle, Sparkles, Pencil } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DailyTask } from '@/types';

interface DailyTaskViewProps {
  task: DailyTask;
  mode: 'planning' | 'learning';
  onToggle: (taskId: string) => void;
  onStartQuiz?: (taskId: string) => void;
  onEdit?: (task: DailyTask) => void;
  isEditable?: boolean;
}

export function DailyTaskView({ task, mode, onToggle, onStartQuiz, onEdit, isEditable = false }: DailyTaskViewProps) {
  const [isHovered, setIsHovered] = useState(false);

  // Mode-specific styles
  const modeStyles = {
    planning: {
      bg: 'bg-white dark:bg-dark-800',
      bgHover: 'hover:bg-primary-50 dark:hover:bg-primary-500/10',
      bgChecked: 'bg-green-50 dark:bg-green-500/10',
      border: 'border-gray-200 dark:border-dark-600',
      borderHover: 'hover:border-primary-300 dark:hover:border-primary-500/50',
      borderChecked: 'border-green-300 dark:border-green-500/50',
      dayBadge: 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400',
      checkHover: 'text-primary-500',
    },
    learning: {
      bg: 'bg-white dark:bg-dark-800',
      bgHover: 'hover:bg-emerald-50 dark:hover:bg-emerald-500/10',
      bgChecked: 'bg-green-50 dark:bg-green-500/10',
      border: 'border-gray-200 dark:border-dark-600',
      borderHover: 'hover:border-emerald-300 dark:hover:border-emerald-500/50',
      borderChecked: 'border-green-300 dark:border-green-500/50',
      dayBadge: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
      checkHover: 'text-emerald-500',
    },
  };

  const currentMode = modeStyles[mode];

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-xl transition-all duration-200 border',
        task.is_checked
          ? cn(currentMode.bgChecked, currentMode.borderChecked)
          : cn(currentMode.bg, currentMode.border, currentMode.bgHover, currentMode.borderHover)
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Day Badge */}
      <div className={cn(
        'flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm',
        task.is_checked
          ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
          : currentMode.dayBadge
      )}>
        D{task.day_number}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={cn(
          'text-sm font-medium',
          task.is_checked
            ? 'text-gray-500 dark:text-gray-400 line-through'
            : 'text-gray-900 dark:text-white'
        )}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
            {task.description}
          </p>
        )}
      </div>

      {/* Action Area */}
      <div className="flex-shrink-0 flex items-center gap-2">
        {/* Edit Button */}
        {isEditable && onEdit && isHovered && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(task);
            }}
            className={cn(
              'p-1.5 rounded-lg transition-all duration-200',
              'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200',
              'hover:bg-gray-100 dark:hover:bg-dark-700'
            )}
          >
            <Pencil className="h-4 w-4" />
          </button>
        )}

        {mode === 'learning' && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onStartQuiz?.(task.id);
            }}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200',
              task.is_checked
                ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
                : 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-500/30 hover:scale-105'
            )}
          >
            {task.is_checked ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5" />
                완료
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                퀴즈 시작
              </>
            )}
          </button>
        )}

        {/* Checkbox */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggle(task.id);
          }}
          className={cn(
            'flex-shrink-0 p-1 rounded-lg transition-all duration-200',
            task.is_checked
              ? 'bg-green-100 dark:bg-green-500/20'
              : isHovered
                ? cn('bg-gray-100 dark:bg-dark-700', currentMode.checkHover)
                : ''
          )}
        >
          {task.is_checked ? (
            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
          ) : (
            <Circle className={cn(
              'h-5 w-5 transition-colors',
              isHovered ? currentMode.checkHover : 'text-gray-300 dark:text-gray-600'
            )} />
          )}
        </button>
      </div>
    </div>
  );
}
