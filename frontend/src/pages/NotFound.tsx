import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

export function NotFound() {
  return (
    <div className="relative min-h-[60vh] flex items-center justify-center">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gray-500/10 dark:bg-gray-500/5 rounded-full blur-3xl" />
      </div>

      <div className="text-center px-4">
        <h1 className="text-8xl md:text-9xl font-bold text-gray-200 dark:text-dark-700 mb-4">
          404
        </h1>

        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4">
          페이지를 찾을 수 없습니다
        </h2>

        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
          요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            to="/"
            className={cn(
              'inline-flex items-center justify-center gap-2 px-6 py-3 font-semibold rounded-xl',
              'text-white bg-gradient-to-r from-primary-600 to-primary-500',
              'hover:from-primary-500 hover:to-primary-400',
              'shadow-lg shadow-primary-500/25',
              'transition-all duration-300'
            )}
          >
            <Home className="w-5 h-5" />
            홈으로 가기
          </Link>

          <button
            onClick={() => window.history.back()}
            className={cn(
              'inline-flex items-center justify-center gap-2 px-6 py-3 font-semibold rounded-xl',
              'text-gray-700 dark:text-gray-300',
              'bg-white dark:bg-dark-800',
              'border border-gray-200 dark:border-dark-700',
              'hover:bg-gray-50 dark:hover:bg-dark-700',
              'transition-all duration-300'
            )}
          >
            <ArrowLeft className="w-5 h-5" />
            뒤로 가기
          </button>
        </div>
      </div>
    </div>
  );
}
