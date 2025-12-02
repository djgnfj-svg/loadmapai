import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  showMenuButton?: boolean;
}

export function Header({ onMenuClick, showMenuButton }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setIsDropdownOpen(false);
    logout();
    navigate('/');
  };

  const handleSettingsClick = () => {
    setIsDropdownOpen(false);
    navigate('/settings');
  };

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
              </nav>
            )}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            {isAuthenticated ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium',
                    'text-gray-700 dark:text-gray-300',
                    'bg-gray-100 dark:bg-dark-700',
                    'hover:bg-gray-200 dark:hover:bg-dark-600',
                    'transition-colors'
                  )}
                >
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">{user?.name}</span>
                  <ChevronDown className={cn(
                    'h-4 w-4 transition-transform',
                    isDropdownOpen && 'rotate-180'
                  )} />
                </button>

                {isDropdownOpen && (
                  <div className={cn(
                    'absolute right-0 mt-2 w-48 py-1 rounded-xl',
                    'bg-white dark:bg-dark-800',
                    'border border-gray-200 dark:border-dark-700',
                    'shadow-lg shadow-gray-200/50 dark:shadow-dark-900/50'
                  )}>
                    <button
                      onClick={handleSettingsClick}
                      className={cn(
                        'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
                        'text-gray-700 dark:text-gray-300',
                        'hover:bg-gray-100 dark:hover:bg-dark-700',
                        'transition-colors'
                      )}
                    >
                      <Settings className="h-4 w-4" />
                      설정
                    </button>
                    <div className="my-1 border-t border-gray-200 dark:border-dark-700" />
                    <button
                      onClick={handleLogout}
                      className={cn(
                        'w-full flex items-center gap-3 px-4 py-2.5 text-sm',
                        'text-red-600 dark:text-red-400',
                        'hover:bg-red-50 dark:hover:bg-red-500/10',
                        'transition-colors'
                      )}
                    >
                      <LogOut className="h-4 w-4" />
                      로그아웃
                    </button>
                  </div>
                )}
              </div>
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
