import { useState } from 'react';
import { User, Moon, Sun, Monitor, Check, Loader2 } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useThemeStore } from '@/stores/themeStore';
import { useToastStore } from '@/stores/toastStore';
import { authApi, getErrorMessage } from '@/lib/api';
import { cn } from '@/lib/utils';

type Theme = 'light' | 'dark' | 'system';

const themeOptions: { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: 'light', label: '라이트', icon: Sun },
  { value: 'dark', label: '다크', icon: Moon },
  { value: 'system', label: '시스템', icon: Monitor },
];

export function Settings() {
  const { user, setUser } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const { success, error: showError } = useToastStore();

  const [name, setName] = useState(user?.name || '');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const handleNameChange = async () => {
    if (!name.trim() || name === user?.name) return;

    setIsLoading(true);
    try {
      const response = await authApi.updateProfile({ name: name.trim() });
      setUser(response.data);
      setIsSaved(true);
      success('이름이 변경되었습니다.');
      setTimeout(() => setIsSaved(false), 2000);
    } catch (error) {
      showError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
        설정
      </h1>

      <div className="space-y-6">
        {/* Profile Section */}
        <section className={cn(
          'p-6 rounded-2xl',
          'bg-white dark:bg-dark-800',
          'border border-gray-200 dark:border-dark-700'
        )}>
          <div className="flex items-center gap-3 mb-6">
            <div className={cn(
              'p-2 rounded-xl',
              'bg-primary-100 dark:bg-primary-500/20'
            )}>
              <User className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              프로필
            </h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                이메일
              </label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className={cn(
                  'w-full px-4 py-2.5 rounded-xl text-sm',
                  'bg-gray-100 dark:bg-dark-700',
                  'text-gray-500 dark:text-gray-400',
                  'border border-gray-200 dark:border-dark-600',
                  'cursor-not-allowed'
                )}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                이름
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="이름을 입력하세요"
                  className={cn(
                    'flex-1 px-4 py-2.5 rounded-xl text-sm',
                    'bg-white dark:bg-dark-700',
                    'text-gray-900 dark:text-white',
                    'border border-gray-200 dark:border-dark-600',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500/50',
                    'transition-all'
                  )}
                />
                <button
                  onClick={handleNameChange}
                  disabled={isLoading || !name.trim() || name === user?.name}
                  className={cn(
                    'px-4 py-2.5 rounded-xl text-sm font-medium',
                    'flex items-center gap-2',
                    'transition-all',
                    isLoading || !name.trim() || name === user?.name
                      ? 'bg-gray-100 dark:bg-dark-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                      : 'bg-primary-600 hover:bg-primary-500 text-white'
                  )}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : isSaved ? (
                    <Check className="h-4 w-4" />
                  ) : null}
                  {isSaved ? '저장됨' : '저장'}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Theme Section */}
        <section className={cn(
          'p-6 rounded-2xl',
          'bg-white dark:bg-dark-800',
          'border border-gray-200 dark:border-dark-700'
        )}>
          <div className="flex items-center gap-3 mb-6">
            <div className={cn(
              'p-2 rounded-xl',
              'bg-primary-100 dark:bg-primary-500/20'
            )}>
              <Moon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              테마
            </h2>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {themeOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = theme === option.value;

              return (
                <button
                  key={option.value}
                  onClick={() => handleThemeChange(option.value)}
                  className={cn(
                    'flex flex-col items-center gap-2 p-4 rounded-xl',
                    'border-2 transition-all',
                    isSelected
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
                      : 'border-gray-200 dark:border-dark-600 hover:border-gray-300 dark:hover:border-dark-500'
                  )}
                >
                  <Icon className={cn(
                    'h-6 w-6',
                    isSelected
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-500 dark:text-gray-400'
                  )} />
                  <span className={cn(
                    'text-sm font-medium',
                    isSelected
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-600 dark:text-gray-400'
                  )}>
                    {option.label}
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}
