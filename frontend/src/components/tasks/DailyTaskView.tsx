import { useState } from 'react';
import { CheckCircle2, Circle, Pencil } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DailyTask } from '@/types';

interface DailyTaskViewProps {
  task: DailyTask;
  onToggle: (taskId: string) => void;
  onEdit?: (task: DailyTask) => void;
  isEditable?: boolean;
}

export function DailyTaskView({ task, onToggle, onEdit, isEditable = false }: DailyTaskViewProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-xl transition-all duration-200 border',
        task.is_checked
          ? 'bg-green-50 dark:bg-green-500/10 border-green-300 dark:border-green-500/50'
          : 'bg-white dark:bg-dark-800 border-gray-200 dark:border-dark-600 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:border-primary-300 dark:hover:border-primary-500/50'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Day Badge */}
      <div className={cn(
        'flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm',
        task.is_checked
          ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
          : 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400'
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
                ? 'bg-gray-100 dark:bg-dark-700 text-primary-500'
                : ''
          )}
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
      </div>
    </div>
  );
}
