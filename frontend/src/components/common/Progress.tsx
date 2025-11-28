import { cn } from '@/lib/utils';

export interface ProgressProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export function Progress({
  value,
  max = 100,
  size = 'md',
  showLabel = false,
  color = 'primary',
  className,
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizes = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  const colors = {
    primary: 'bg-primary-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-500',
    danger: 'bg-red-600',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className={cn('w-full bg-gray-200 dark:bg-dark-600 rounded-full overflow-hidden', sizes[size])}>
        <div
          className={cn(
            'h-full rounded-full transition-all duration-300 ease-out',
            colors[color]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="mt-1 flex justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>{Math.round(percentage)}% 완료</span>
          <span>{value}/{max}</span>
        </div>
      )}
    </div>
  );
}

export interface CircularProgressProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export function CircularProgress({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  showLabel = true,
  color = 'primary',
  className,
}: CircularProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const colors = {
    primary: 'text-primary-600',
    success: 'text-green-600',
    warning: 'text-yellow-500',
    danger: 'text-red-600',
  };

  // Dynamic font size based on circle size
  const getFontSize = () => {
    if (size <= 60) return 'text-sm';
    if (size <= 80) return 'text-base';
    if (size <= 100) return 'text-lg';
    if (size <= 120) return 'text-xl';
    return 'text-2xl';
  };

  const getSubFontSize = () => {
    if (size <= 60) return 'text-[10px]';
    if (size <= 100) return 'text-xs';
    return 'text-sm';
  };

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-200 dark:text-dark-600"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn('transition-all duration-500 ease-out', colors[color])}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn('font-bold text-gray-900 dark:text-white', getFontSize())}>
            {Math.round(percentage)}%
          </span>
          <span className={cn('text-gray-500 dark:text-gray-400', getSubFontSize())}>완료</span>
        </div>
      )}
    </div>
  );
}
