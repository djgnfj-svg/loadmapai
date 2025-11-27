import { NavLink, useLocation } from 'react-router-dom';
import {
  Home,
  Map,
  GraduationCap,
  PlusCircle,
  Settings,
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

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <nav className="flex flex-col h-full px-4 py-6">
        <div className="flex-1 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href ||
              (item.href !== '/dashboard' && location.pathname.startsWith(item.href));

            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={cn(
                    'h-5 w-5',
                    isActive ? 'text-primary-600' : 'text-gray-400'
                  )}
                />
                {item.name}
              </NavLink>
            );
          })}
        </div>

        <div className="pt-6 mt-6 border-t border-gray-200 space-y-1">
          {secondaryNavigation.map((item) => {
            const isActive = location.pathname === item.href;

            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <item.icon
                  className={cn(
                    'h-5 w-5',
                    isActive ? 'text-primary-600' : 'text-gray-400'
                  )}
                />
                {item.name}
              </NavLink>
            );
          })}
        </div>
      </nav>
    </aside>
  );
}
