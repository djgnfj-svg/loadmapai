import { Link } from 'react-router-dom';
import { Menu, User, LogOut } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { ThemeToggle } from '@/components/common/ThemeToggle';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  showMenuButton?: boolean;
}

export function Header({ onMenuClick, showMenuButton }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <header className={cn(
      'fixed top-0 left-0 right-0 z-30',
      'bg-white/80 dark:bg-dark-900/80 backdrop-blur-xl',
      'border-b border-gray-200 dark:border-dark-700'
    )}>
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-4">
            {showMenuButton && (
              <button
                onClick={onMenuClick}
                className={cn(
                  'p-2 rounded-xl lg:hidden',
                  'hover:bg-gray-100 dark:hover:bg-dark-700',
                  'transition-colors'
                )}
                aria-label="메뉴 열기"
              >
                <Menu className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
            )}

            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">L</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-500 dark:from-primary-400 dark:to-primary-300 bg-clip-text text-transparent">
                LoadmapAI
              </span>
            </Link>

            {isAuthenticated && (
              <nav className="hidden md:flex ml-6 items-center space-x-1">
                <Link
                  to="/roadmaps"
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-medium',
                    'text-gray-600 dark:text-gray-400',
                    'hover:text-gray-900 dark:hover:text-white',
                    'hover:bg-gray-100 dark:hover:bg-dark-700',
                    'transition-colors'
                  )}
                >
                  로드맵
                </Link>
                <Link
                  to="/learning"
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-medium',
                    'text-gray-600 dark:text-gray-400',
                    'hover:text-gray-900 dark:hover:text-white',
                    'hover:bg-gray-100 dark:hover:bg-dark-700',
                    'transition-colors'
                  )}
                >
                  학습
                </Link>
              </nav>
            )}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />

            {isAuthenticated ? (
              <>
                <div className={cn(
                  'hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl',
                  'bg-gray-100 dark:bg-dark-700',
                  'text-sm text-gray-600 dark:text-gray-400'
                )}>
                  <User className="h-4 w-4" />
                  <span>{user?.name}</span>
                </div>
                <button
                  onClick={logout}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium',
                    'text-gray-700 dark:text-gray-300',
                    'bg-gray-100 dark:bg-dark-700',
                    'hover:bg-gray-200 dark:hover:bg-dark-600',
                    'transition-colors'
                  )}
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">로그아웃</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-medium',
                    'text-gray-600 dark:text-gray-400',
                    'hover:text-gray-900 dark:hover:text-white',
                    'hover:bg-gray-100 dark:hover:bg-dark-700',
                    'transition-colors'
                  )}
                >
                  로그인
                </Link>
                <Link
                  to="/register"
                  className={cn(
                    'px-4 py-2 rounded-xl text-sm font-medium',
                    'text-white',
                    'bg-gradient-to-r from-primary-600 to-primary-500',
                    'hover:from-primary-500 hover:to-primary-400',
                    'shadow-lg shadow-primary-500/25',
                    'transition-all'
                  )}
                >
                  회원가입
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
