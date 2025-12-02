import { useState } from 'react';
import { ChevronDown, CheckCircle2, Circle, Pencil } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DailyTask } from '@/types';

interface DayGroupViewProps {
  dayNumber: number;
  tasks: DailyTask[];
  defaultExpanded?: boolean;
  onToggleTask: (taskId: string) => void;
  isEditable?: boolean;
  onEditTask?: (task: DailyTask) => void;
}

export function DayGroupView({
  dayNumber,
  tasks,
  defaultExpanded = false,
  onToggleTask,
  isEditable = false,
  onEditTask,
}: DayGroupViewProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const completedCount = tasks.filter(t => t.is_checked).length;
  const totalCount = tasks.length;
  const isAllComplete = completedCount === totalCount && totalCount > 0;

  // 요일 이름 (1=월, 2=화, ...)
  const dayNames = ['', '월', '화', '수', '목', '금', '토', '일'];
  const dayName = dayNames[dayNumber] || '';

  return (
    <div
      className={cn(
        'rounded-lg overflow-hidden transition-all duration-200 border',
        isAllComplete
          ? 'bg-green-50/50 dark:bg-green-500/5 border-green-200 dark:border-green-500/30'
          : 'bg-white dark:bg-dark-700 border-gray-200 dark:border-dark-500'
      )}
    >
      {/* Day Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left"
      >
        <div className="px-3 py-2.5 flex items-center gap-3">
          {/* Day Badge */}
          <div className={cn(
            'flex-shrink-0 w-12 h-8 rounded-md flex items-center justify-center font-semibold text-sm gap-1',
            isAllComplete
              ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
              : 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-400'
          )}>
            <span>D{dayNumber}</span>
            {dayName && <span className="text-xs opacity-70">({dayName})</span>}
          </div>

          {/* Progress Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {dayNumber}일차
              </span>
              {isAllComplete && (
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
              )}
            </div>
          </div>

          {/* Task Count & Chevron */}
          <div className="flex items-center gap-2">
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              isAllComplete
                ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400'
                : 'bg-gray-100 dark:bg-dark-600 text-gray-600 dark:text-gray-400'
            )}>
              {completedCount}/{totalCount}
            </span>
            <div className={cn(
              'p-1 rounded transition-transform duration-200',
              isExpanded && 'rotate-180'
            )}>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </div>
          </div>
        </div>
      </button>

      {/* Tasks List */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-200 ease-in-out',
          isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <div className="px-3 pb-3 space-y-1.5">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={onToggleTask}
              isEditable={isEditable}
              onEdit={onEditTask}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// Individual task item within a day group
interface TaskItemProps {
  task: DailyTask;
  onToggle: (taskId: string) => void;
  isEditable?: boolean;
  onEdit?: (task: DailyTask) => void;
}

function TaskItem({ task, onToggle, isEditable = false, onEdit }: TaskItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={cn(
        'flex items-center gap-2 p-2 rounded-lg transition-all duration-150',
        task.is_checked
          ? 'bg-green-50 dark:bg-green-500/10'
          : 'bg-gray-50 dark:bg-dark-600 hover:bg-primary-50 dark:hover:bg-primary-500/10'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Checkbox */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onToggle(task.id);
        }}
        className="flex-shrink-0 p-0.5"
      >
        {task.is_checked ? (
          <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
        ) : (
          <Circle className={cn(
            'h-5 w-5 transition-colors',
            isHovered ? 'text-primary-500' : 'text-gray-300 dark:text-gray-500'
          )} />
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={cn(
          'text-sm',
          task.is_checked
            ? 'text-gray-500 dark:text-gray-400 line-through'
            : 'text-gray-800 dark:text-gray-100'
        )}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
            {task.description}
          </p>
        )}
      </div>

      {/* Edit Button */}
      {isEditable && onEdit && isHovered && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit(task);
          }}
          className={cn(
            'flex-shrink-0 p-1 rounded transition-colors',
            'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200',
            'hover:bg-gray-200 dark:hover:bg-dark-500'
          )}
        >
          <Pencil className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
