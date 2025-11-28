import { useEffect, useState } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

const icons = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const styles = {
  success: cn(
    'bg-green-50 dark:bg-green-500/10',
    'border-green-200 dark:border-green-500/30',
    'text-green-800 dark:text-green-300'
  ),
  error: cn(
    'bg-red-50 dark:bg-red-500/10',
    'border-red-200 dark:border-red-500/30',
    'text-red-800 dark:text-red-300'
  ),
  warning: cn(
    'bg-yellow-50 dark:bg-yellow-500/10',
    'border-yellow-200 dark:border-yellow-500/30',
    'text-yellow-800 dark:text-yellow-300'
  ),
  info: cn(
    'bg-blue-50 dark:bg-blue-500/10',
    'border-blue-200 dark:border-blue-500/30',
    'text-blue-800 dark:text-blue-300'
  ),
};

const iconStyles = {
  success: 'text-green-500 dark:text-green-400',
  error: 'text-red-500 dark:text-red-400',
  warning: 'text-yellow-500 dark:text-yellow-400',
  info: 'text-blue-500 dark:text-blue-400',
};

export function Toast({ id, type, message, duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);
  const Icon = icons[type];

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onClose(id), 300);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose(id), 300);
  };

  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-xl border',
        'shadow-lg dark:shadow-dark-900/50',
        'backdrop-blur-sm',
        'transition-all duration-300',
        styles[type],
        isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      )}
    >
      <Icon className={cn('h-5 w-5 flex-shrink-0 mt-0.5', iconStyles[type])} />
      <p className="flex-1 text-sm font-medium">{message}</p>
      <button
        onClick={handleClose}
        className={cn(
          'flex-shrink-0 p-1 rounded-lg',
          'hover:bg-black/5 dark:hover:bg-white/10',
          'transition-colors'
        )}
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: Array<Omit<ToastProps, 'onClose'>>;
  onClose: (id: string) => void;
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  );
}
