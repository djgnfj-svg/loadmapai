/**
 * Roadmap status related constants
 */

export const STATUS_COLORS = {
  ACTIVE: 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-400',
  COMPLETED: 'bg-blue-100 dark:bg-blue-500/20 text-blue-800 dark:text-blue-400',
  PAUSED: 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-800 dark:text-yellow-400',
} as const;

export const STATUS_LABELS = {
  ACTIVE: '진행 중',
  COMPLETED: '완료',
  PAUSED: '일시정지',
} as const;

export type RoadmapStatusKey = keyof typeof STATUS_COLORS;
