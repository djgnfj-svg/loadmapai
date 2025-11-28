import { useState, useEffect } from 'react';
import { X, Save, Trash2, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { cn } from '@/lib/utils';

interface EditTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'monthly' | 'weekly' | 'daily';
  title: string;
  description: string;
  dayNumber?: number;
  onSave: (data: { title: string; description: string; day_number?: number }) => void;
  onDelete?: () => void;
  isLoading?: boolean;
  showFinalizeWarning?: boolean;
}

export function EditTaskModal({
  isOpen,
  onClose,
  type,
  title: initialTitle,
  description: initialDescription,
  dayNumber: initialDayNumber,
  onSave,
  onDelete,
  isLoading,
  showFinalizeWarning,
}: EditTaskModalProps) {
  const [title, setTitle] = useState(initialTitle);
  const [description, setDescription] = useState(initialDescription);
  const [dayNumber, setDayNumber] = useState(initialDayNumber || 1);

  useEffect(() => {
    setTitle(initialTitle);
    setDescription(initialDescription);
    setDayNumber(initialDayNumber || 1);
  }, [initialTitle, initialDescription, initialDayNumber]);

  if (!isOpen) return null;

  const typeLabels = {
    monthly: '월간 목표',
    weekly: '주간 태스크',
    daily: '일일 태스크',
  };

  const handleSave = () => {
    const data: { title: string; description: string; day_number?: number } = {
      title,
      description,
    };
    if (type === 'daily') {
      data.day_number = dayNumber;
    }
    onSave(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-dark-800 rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {typeLabels[type]} 편집
          </h3>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Finalize Warning */}
        {showFinalizeWarning && (
          <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/30 rounded-lg flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              확정된 로드맵을 수정하고 있습니다. 수정 횟수가 기록됩니다.
            </p>
          </div>
        )}

        {/* Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              제목
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="제목을 입력하세요"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              설명
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="설명을 입력하세요 (선택)"
              rows={3}
              className={cn(
                'w-full px-3 py-2 rounded-lg border',
                'bg-white dark:bg-dark-700',
                'border-gray-300 dark:border-dark-600',
                'text-gray-900 dark:text-white',
                'placeholder-gray-400 dark:placeholder-gray-500',
                'focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'transition-colors resize-none'
              )}
            />
          </div>

          {type === 'daily' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                요일 (Day)
              </label>
              <select
                value={dayNumber}
                onChange={(e) => setDayNumber(Number(e.target.value))}
                className={cn(
                  'w-full px-3 py-2 rounded-lg border',
                  'bg-white dark:bg-dark-700',
                  'border-gray-300 dark:border-dark-600',
                  'text-gray-900 dark:text-white',
                  'focus:ring-2 focus:ring-primary-500 focus:border-transparent'
                )}
              >
                {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                  <option key={d} value={d}>
                    Day {d}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mt-6">
          {onDelete ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDelete}
              disabled={isLoading}
              className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              삭제
            </Button>
          ) : (
            <div />
          )}

          <div className="flex gap-2">
            <Button
              variant="ghost"
              onClick={onClose}
              disabled={isLoading}
            >
              취소
            </Button>
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={isLoading || !title.trim()}
            >
              <Save className="h-4 w-4 mr-1" />
              저장
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
