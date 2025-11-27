import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

export function Header() {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-primary-600">
              LoadmapAI
            </Link>
            {isAuthenticated && (
              <nav className="ml-10 flex items-center space-x-4">
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

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-gray-600">{user?.name}</span>
                <button
                  onClick={logout}
                  className={cn(
                    'px-4 py-2 text-sm font-medium rounded-md',
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
                    'px-4 py-2 text-sm font-medium rounded-md',
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
