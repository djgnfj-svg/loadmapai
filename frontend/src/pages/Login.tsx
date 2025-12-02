import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/lib/api';
import { cn } from '@/lib/utils';
import { Mail, Lock, AlertCircle } from 'lucide-react';
import type { AxiosError } from 'axios';

export function Login() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await authApi.login({ email, password });
      const { user, access_token, refresh_token } = response.data;
      login(user, access_token);
      localStorage.setItem('refresh_token', refresh_token);
      navigate('/roadmaps');
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      setError(axiosError.response?.data?.detail || '로그인에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className={cn(
          'px-8 py-10 rounded-2xl',
          'bg-white dark:bg-dark-800',
          'border border-gray-100 dark:border-dark-700',
          'shadow-xl shadow-gray-200/50 dark:shadow-dark-900/50'
        )}>
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              다시 오신 것을 환영합니다
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              계정에 로그인하세요
            </p>
          </div>

          {error && (
            <div className={cn(
              'mb-6 p-4 rounded-xl flex items-start gap-3',
              'bg-red-50 dark:bg-red-500/10',
              'border border-red-200 dark:border-red-500/30',
              'text-red-600 dark:text-red-400 text-sm'
            )}>
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                이메일
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className={cn(
                    'w-full pl-12 pr-4 py-3 rounded-xl',
                    'bg-white dark:bg-dark-700',
                    'border border-gray-200 dark:border-dark-600',
                    'text-gray-900 dark:text-white',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                    'focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400',
                    'transition-all duration-200'
                  )}
                  placeholder="example@email.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                비밀번호
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className={cn(
                    'w-full pl-12 pr-4 py-3 rounded-xl',
                    'bg-white dark:bg-dark-700',
                    'border border-gray-200 dark:border-dark-600',
                    'text-gray-900 dark:text-white',
                    'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                    'focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 dark:focus:border-primary-400',
                    'transition-all duration-200'
                  )}
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                'w-full py-3 rounded-xl font-semibold',
                'text-white',
                'bg-gradient-to-r from-primary-600 to-primary-500',
                'hover:from-primary-500 hover:to-primary-400',
                'shadow-lg shadow-primary-500/25',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-all duration-200'
              )}
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            계정이 없으신가요?{' '}
            <Link to="/register" className="text-primary-600 dark:text-primary-400 hover:underline font-semibold">
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
