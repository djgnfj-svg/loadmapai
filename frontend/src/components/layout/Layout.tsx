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

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  // Close sidebar on window resize to desktop
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
    <div className="min-h-screen bg-gray-50">
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
