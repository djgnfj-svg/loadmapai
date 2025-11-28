import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

export function Layout() {
  const { isAuthenticated } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className={cn(
      'min-h-screen',
      'bg-gray-50 dark:bg-dark-900',
      'transition-colors duration-300'
    )}>
      <Header
        onMenuClick={() => setSidebarOpen(true)}
        showMenuButton={isAuthenticated}
      />
      {isAuthenticated && (
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
      )}
      <main
        className={cn(
          'pt-16 min-h-screen',
          'py-8 px-4 sm:px-6 lg:px-8',
          isAuthenticated ? 'lg:ml-64' : 'max-w-7xl mx-auto'
        )}
      >
        <Outlet />
      </main>
    </div>
  );
}
