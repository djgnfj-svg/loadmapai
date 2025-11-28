import { Link } from 'react-router-dom';
import { Menu, User } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  showMenuButton?: boolean;
}

export function Header({ onMenuClick, showMenuButton }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <header className="fixed top-0 left-0 right-0 z-30 bg-white border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-4">
            {/* Mobile menu button */}
            {showMenuButton && (
              <button
                onClick={onMenuClick}
                className="p-2 rounded-lg hover:bg-gray-100 lg:hidden"
                aria-label="메뉴 열기"
              >
                <Menu className="h-5 w-5 text-gray-600" />
              </button>
            )}

            <Link to="/" className="text-xl font-bold text-primary-600">
              LoadmapAI
            </Link>

            {/* Desktop navigation - hidden on mobile */}
            {isAuthenticated && (
              <nav className="hidden md:flex ml-6 items-center space-x-4">
                <Link
                  to="/roadmaps"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  로드맵
                </Link>
                <Link
                  to="/learning"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  학습
                </Link>
              </nav>
            )}
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {isAuthenticated ? (
              <>
                {/* User info - hidden on mobile */}
                <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
                  <User className="h-4 w-4" />
                  <span>{user?.name}</span>
                </div>
                <button
                  onClick={logout}
                  className={cn(
                    'px-3 py-1.5 sm:px-4 sm:py-2 text-sm font-medium rounded-md',
                    'text-gray-700 bg-gray-100 hover:bg-gray-200'
                  )}
                >
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  로그인
                </Link>
                <Link
                  to="/register"
                  className={cn(
                    'px-3 py-1.5 sm:px-4 sm:py-2 text-sm font-medium rounded-md',
                    'text-white bg-primary-600 hover:bg-primary-700'
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
