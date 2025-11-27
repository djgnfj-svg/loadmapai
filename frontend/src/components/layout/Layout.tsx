import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

export function Layout() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      {isAuthenticated && <Sidebar />}
      <main
        className={cn(
          'py-8 px-4 sm:px-6 lg:px-8',
          isAuthenticated ? 'ml-64' : 'max-w-7xl mx-auto'
        )}
      >
        <Outlet />
      </main>
    </div>
  );
}
