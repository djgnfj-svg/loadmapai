import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Check, X, Loader2, MessageSquare, Zap } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { cn } from '@/lib/utils';
import {
  useChatHistory,
  useQuickActions,
  useSendChatMessage,
  useSendQuickAction,
  useApplyChanges,
} from '@/hooks';
import type { ChatChangeItem, ChatMessageResponse } from '@/types';

interface ChatPanelProps {
  roadmapId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function ChatPanel({ roadmapId, isOpen, onClose }: ChatPanelProps) {
  const [message, setMessage] = useState('');
  const [pendingChanges, setPendingChanges] = useState<ChatChangeItem[]>([]);
  const [selectedChangeIds, setSelectedChangeIds] = useState<Set<string>>(new Set());
  const [lastResponse, setLastResponse] = useState<string>('');
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: history = [] } = useChatHistory(roadmapId);
  const { data: quickActions = [] } = useQuickActions(roadmapId);

  const sendMessage = useSendChatMessage(roadmapId);
  const sendQuickAction = useSendQuickAction(roadmapId);
  const applyChanges = useApplyChanges(roadmapId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, lastResponse]);

  if (!isOpen) return null;

  const handleSendMessage = async () => {
    if (!message.trim() || sendMessage.isPending) return;

    const messageToSend = message;
    setMessage('');

    try {
      const response = await sendMessage.mutateAsync({ message: messageToSend });
      const data = response.data as ChatMessageResponse;

      setLastResponse(data.message);
      setSuggestions(data.suggestions || []);

      if (data.changes && data.changes.length > 0) {
        setPendingChanges(data.changes);
        setSelectedChangeIds(new Set(data.changes.map((c) => c.id)));
      } else {
        setPendingChanges([]);
        setSelectedChangeIds(new Set());
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleQuickAction = async (action: string) => {
    if (sendQuickAction.isPending) return;

    try {
      const response = await sendQuickAction.mutateAsync(action);
      const data = response.data as ChatMessageResponse;

      setLastResponse(data.message);
      setSuggestions(data.suggestions || []);

      if (data.changes && data.changes.length > 0) {
        setPendingChanges(data.changes);
        setSelectedChangeIds(new Set(data.changes.map((c) => c.id)));
      }
    } catch (error) {
      console.error('Failed to send quick action:', error);
    }
  };

  const handleApplyChanges = async () => {
    if (pendingChanges.length === 0 || applyChanges.isPending) return;

    const changesToApply = pendingChanges.filter((c) =>
      selectedChangeIds.has(c.id)
    );

    try {
      await applyChanges.mutateAsync({
        change_ids: Array.from(selectedChangeIds),
        changes: changesToApply,
      });

      setPendingChanges([]);
      setSelectedChangeIds(new Set());
      setLastResponse('변경사항이 적용되었습니다!');
    } catch (error) {
      console.error('Failed to apply changes:', error);
    }
  };

  const toggleChangeSelection = (changeId: string) => {
    const newSelected = new Set(selectedChangeIds);
    if (newSelected.has(changeId)) {
      newSelected.delete(changeId);
    } else {
      newSelected.add(changeId);
    }
    setSelectedChangeIds(newSelected);
  };

  const getActionLabel = (action: string) => {
    switch (action) {
      case 'modify':
        return '수정';
      case 'add':
        return '추가';
      case 'delete':
        return '삭제';
      default:
        return action;
    }
  };

  const getTargetTypeLabel = (type: string) => {
    switch (type) {
      case 'daily':
        return '일일';
      case 'weekly':
        return '주간';
      case 'monthly':
        return '월간';
      case 'roadmap':
        return '로드맵';
      default:
        return type;
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-dark-800 shadow-xl z-40 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-600">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-gray-900 dark:text-white">
            AI 편집 도우미
          </h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Quick Actions */}
      <div className="p-3 border-b border-gray-200 dark:border-dark-600">
        <div className="flex items-center gap-1.5 mb-2 text-xs text-gray-500 dark:text-gray-400">
          <Zap className="h-3.5 w-3.5" />
          빠른 액션
        </div>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action) => (
            <button
              key={action}
              onClick={() => handleQuickAction(action)}
              disabled={sendQuickAction.isPending}
              className={cn(
                'px-2.5 py-1.5 text-xs font-medium rounded-lg transition-colors',
                'bg-primary-50 dark:bg-primary-500/10',
                'text-primary-700 dark:text-primary-400',
                'hover:bg-primary-100 dark:hover:bg-primary-500/20',
                'disabled:opacity-50'
              )}
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {history.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              'p-3 rounded-lg',
              msg.role === 'user'
                ? 'bg-primary-50 dark:bg-primary-500/10 ml-8'
                : 'bg-gray-100 dark:bg-dark-700 mr-8'
            )}
          >
            <p className="text-sm text-gray-900 dark:text-white">
              {msg.content}
            </p>
          </div>
        ))}

        {/* Last Response (with changes) */}
        {lastResponse && (
          <div className="bg-gray-100 dark:bg-dark-700 p-3 rounded-lg mr-8">
            <div className="flex items-start gap-2">
              <Sparkles className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-gray-900 dark:text-white">
                {lastResponse}
              </p>
            </div>
          </div>
        )}

        {/* Pending Changes */}
        {pendingChanges.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-500/10 p-3 rounded-lg border border-blue-200 dark:border-blue-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-blue-800 dark:text-blue-300">
                제안된 변경사항
              </span>
              <span className="text-xs text-blue-600 dark:text-blue-400">
                {selectedChangeIds.size}/{pendingChanges.length} 선택됨
              </span>
            </div>

            <div className="space-y-2">
              {pendingChanges.map((change) => (
                <label
                  key={change.id}
                  className={cn(
                    'flex items-start gap-2 p-2 rounded-lg cursor-pointer transition-colors',
                    selectedChangeIds.has(change.id)
                      ? 'bg-blue-100 dark:bg-blue-500/20'
                      : 'bg-white dark:bg-dark-700'
                  )}
                >
                  <input
                    type="checkbox"
                    checked={selectedChangeIds.has(change.id)}
                    onChange={() => toggleChangeSelection(change.id)}
                    className="mt-0.5"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className={cn(
                        'px-1.5 py-0.5 rounded font-medium',
                        change.action === 'modify' && 'bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400',
                        change.action === 'add' && 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400',
                        change.action === 'delete' && 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400'
                      )}>
                        {getActionLabel(change.action)}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {getTargetTypeLabel(change.target_type)}
                      </span>
                    </div>
                    {change.action === 'modify' && (
                      <div className="mt-1 text-xs">
                        <span className="text-gray-500 dark:text-gray-400 line-through">
                          {change.old_value}
                        </span>
                        <span className="mx-1">→</span>
                        <span className="text-gray-900 dark:text-white">
                          {change.new_value}
                        </span>
                      </div>
                    )}
                    {change.action === 'add' && (
                      <div className="mt-1 text-xs text-gray-900 dark:text-white">
                        + {change.new_value}
                      </div>
                    )}
                  </div>
                </label>
              ))}
            </div>

            <div className="flex gap-2 mt-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setPendingChanges([]);
                  setSelectedChangeIds(new Set());
                }}
                className="flex-1"
              >
                <X className="h-4 w-4 mr-1" />
                취소
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleApplyChanges}
                disabled={selectedChangeIds.size === 0 || applyChanges.isPending}
                className="flex-1"
              >
                {applyChanges.isPending ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Check className="h-4 w-4 mr-1" />
                )}
                적용
              </Button>
            </div>
          </div>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && pendingChanges.length === 0 && (
          <div className="space-y-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              추가 제안
            </span>
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => setMessage(suggestion)}
                className={cn(
                  'w-full text-left p-2 text-xs rounded-lg transition-colors',
                  'bg-gray-50 dark:bg-dark-700',
                  'text-gray-700 dark:text-gray-300',
                  'hover:bg-gray-100 dark:hover:bg-dark-600'
                )}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-dark-600">
        <div className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="예: D3 태스크를 쉽게 바꿔줘"
            className="flex-1"
          />
          <Button
            variant="primary"
            onClick={handleSendMessage}
            disabled={!message.trim() || sendMessage.isPending}
          >
            {sendMessage.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
