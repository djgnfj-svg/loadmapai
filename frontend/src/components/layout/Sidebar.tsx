import { NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  Map,
  GraduationCap,
  PlusCircle,
  Settings,
  X,
  LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: LucideIcon;
}

const navigation: NavItem[] = [
  { name: '대시보드', href: '/dashboard', icon: Home },
  { name: '내 로드맵', href: '/roadmaps', icon: Map },
  { name: '새 로드맵', href: '/roadmaps/create', icon: PlusCircle },
  { name: '학습하기', href: '/learning', icon: GraduationCap },
];

const secondaryNavigation: NavItem[] = [
  { name: '설정', href: '/settings', icon: Settings },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const location = useLocation();

  const handleNavClick = () => {
    if (onClose && window.innerWidth < 1024) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-16 bottom-0 w-64 z-50',
          'bg-white dark:bg-dark-800',
          'border-r border-gray-200 dark:border-dark-700',
          'overflow-y-auto custom-scrollbar',
          'transform transition-transform duration-300 ease-out',
          'lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile close button */}
        <button
          onClick={onClose}
          className={cn(
            'absolute top-4 right-4 p-2 rounded-xl lg:hidden',
            'hover:bg-gray-100 dark:hover:bg-dark-700',
            'transition-colors'
          )}
        >
          <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
        </button>

        <nav className="flex flex-col h-full px-4 py-6">
          <div className="flex-1 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href ||
                (item.href !== '/dashboard' && location.pathname.startsWith(item.href));

              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={handleNavClick}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium',
                    'transition-all duration-200',
                    isActive
                      ? cn(
                          'bg-primary-50 dark:bg-primary-500/10',
                          'text-primary-700 dark:text-primary-400',
                          'shadow-sm'
                        )
                      : cn(
                          'text-gray-600 dark:text-gray-400',
                          'hover:bg-gray-100 dark:hover:bg-dark-700',
                          'hover:text-gray-900 dark:hover:text-white'
                        )
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5',
                      isActive
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-gray-400 dark:text-gray-500'
                    )}
                  />
                  {item.name}
                </NavLink>
              );
            })}
          </div>

          <div className="pt-6 mt-6 border-t border-gray-200 dark:border-dark-700 space-y-1">
            {secondaryNavigation.map((item) => {
              const isActive = location.pathname === item.href;

              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={handleNavClick}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium',
                    'transition-all duration-200',
                    isActive
                      ? cn(
                          'bg-primary-50 dark:bg-primary-500/10',
                          'text-primary-700 dark:text-primary-400',
                          'shadow-sm'
                        )
                      : cn(
                          'text-gray-600 dark:text-gray-400',
                          'hover:bg-gray-100 dark:hover:bg-dark-700',
                          'hover:text-gray-900 dark:hover:text-white'
                        )
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5',
                      isActive
                        ? 'text-primary-600 dark:text-primary-400'
                        : 'text-gray-400 dark:text-gray-500'
                    )}
                  />
                  {item.name}
                </NavLink>
              );
            })}
          </div>
        </nav>
      </aside>
    </>
  );
}
