import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading,
      leftIcon,
      rightIcon,
      fullWidth,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles = cn(
      'inline-flex items-center justify-center gap-2 font-semibold rounded-xl',
      'transition-all duration-200 ease-out',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'focus:ring-offset-white dark:focus:ring-offset-dark-900',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
      'active:scale-[0.98]'
    );

    const variants = {
      primary: cn(
        'bg-gradient-to-r from-primary-600 to-primary-500',
        'hover:from-primary-500 hover:to-primary-400',
        'text-white shadow-lg shadow-primary-500/25',
        'hover:shadow-xl hover:shadow-primary-500/30',
        'focus:ring-primary-500',
        'dark:from-primary-500 dark:to-primary-400',
        'dark:hover:from-primary-400 dark:hover:to-primary-300'
      ),
      secondary: cn(
        'bg-gray-100 dark:bg-dark-700',
        'text-gray-900 dark:text-gray-100',
        'hover:bg-gray-200 dark:hover:bg-dark-600',
        'focus:ring-gray-500',
        'border border-gray-200 dark:border-dark-600'
      ),
      outline: cn(
        'border-2 border-primary-500 dark:border-primary-400',
        'text-primary-600 dark:text-primary-400',
        'hover:bg-primary-50 dark:hover:bg-primary-500/10',
        'focus:ring-primary-500'
      ),
      ghost: cn(
        'text-gray-700 dark:text-gray-300',
        'hover:bg-gray-100 dark:hover:bg-dark-700',
        'focus:ring-gray-500'
      ),
      danger: cn(
        'bg-gradient-to-r from-red-600 to-red-500',
        'hover:from-red-500 hover:to-red-400',
        'text-white shadow-lg shadow-red-500/25',
        'hover:shadow-xl hover:shadow-red-500/30',
        'focus:ring-red-500'
      ),
      success: cn(
        'bg-gradient-to-r from-secondary-600 to-secondary-500',
        'hover:from-secondary-500 hover:to-secondary-400',
        'text-white shadow-lg shadow-secondary-500/25',
        'hover:shadow-xl hover:shadow-secondary-500/30',
        'focus:ring-secondary-500'
      ),
    };

    const sizes = {
      xs: 'px-2.5 py-1.5 text-xs',
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-2.5 text-sm',
      lg: 'px-5 py-3 text-base',
      xl: 'px-6 py-3.5 text-lg',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>로딩 중...</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
