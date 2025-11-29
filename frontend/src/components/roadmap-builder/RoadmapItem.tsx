import { cn } from '../../lib/utils';
import type { RoadmapItemWithStatus } from '../../types';

interface RoadmapItemProps {
  item: RoadmapItemWithStatus;
  className?: string;
  as?: 'span' | 'p' | 'h3' | 'h4';
}

export function RoadmapItem({ item, className, as: Component = 'span' }: RoadmapItemProps) {
  if (item.status === 'undefined') {
    return (
      <Component
        className={cn(
          'text-gray-400 dark:text-gray-500 animate-pulse font-mono',
          className
        )}
      >
        ???
      </Component>
    );
  }

  return (
    <Component
      className={cn(
        'transition-all duration-300',
        item.isNew && 'bg-green-100 dark:bg-green-900/30 rounded px-1 animate-fade-in',
        item.status === 'partial' && 'text-yellow-600 dark:text-yellow-400',
        item.status === 'confirmed' && 'text-gray-900 dark:text-gray-100',
        className
      )}
    >
      {item.content}
    </Component>
  );
}
