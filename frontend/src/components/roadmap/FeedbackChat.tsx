/**
 * 피드백 채팅 컴포넌트
 *
 * 로드맵 생성 후 사용자와 대화하며 로드맵을 개선합니다.
 */
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Loader2,
  CheckCircle2,
  X,
  Sparkles,
  Calendar,
  Edit3,
  ChevronDown,
  ChevronRight,
  Bot,
  User,
  Lightbulb,
} from 'lucide-react';
import { Button } from '@/components/common/Button';
import { cn } from '@/lib/utils';
import type { FeedbackMessage, RoadmapPreviewData, RoadmapModifications } from '@/types/feedback';

interface FeedbackChatProps {
  messages: FeedbackMessage[];
  roadmapData: RoadmapPreviewData | null;
  onSendMessage: (message: string) => void;
  onFinalize: () => void;
  onCancel: () => void;
  isLoading: boolean;
  error: string | null;
}

export function FeedbackChat({
  messages,
  roadmapData,
  onSendMessage,
  onFinalize,
  onCancel,
  isLoading,
  error,
}: FeedbackChatProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 새 메시지가 오면 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  // 빠른 피드백 제안
  const quickSuggestions = [
    { text: '너무 어려워요', icon: '😅' },
    { text: '더 쉽게 해주세요', icon: '📚' },
    { text: '실습 위주로', icon: '💻' },
    { text: '이론 위주로', icon: '📖' },
    { text: '기간 늘려주세요', icon: '📅' },
    { text: '더 빡세게', icon: '🔥' },
  ];

  return (
    <div className="h-[calc(100vh-180px)] min-h-[500px] flex flex-col lg:flex-row gap-6">
      {/* 왼쪽: 채팅 영역 */}
      <div className="w-full lg:w-[480px] flex-shrink-0 order-1">
        <div className="h-full bg-white dark:bg-dark-800 rounded-2xl border border-gray-200 dark:border-dark-600 shadow-lg flex flex-col overflow-hidden">
          {/* 헤더 */}
          <div className="px-5 py-4 border-b border-gray-200 dark:border-dark-600 bg-gradient-to-r from-indigo-500 to-purple-600">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-white/20 backdrop-blur-sm">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-white">
                  AI 어시스턴트
                </h3>
                <p className="text-xs text-white/80">
                  로드맵을 함께 다듬어요
                </p>
              </div>
              <div className="ml-auto flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-xs text-white/80">온라인</span>
              </div>
            </div>
          </div>

          {/* 메시지 영역 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-dark-900/50">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
            </AnimatePresence>

            {isLoading && <TypingIndicator />}

            <div ref={messagesEndRef} />
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="mx-4 mb-3 p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-xl">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* 하단 입력 영역 */}
          <div className="p-4 border-t border-gray-200 dark:border-dark-600 bg-white dark:bg-dark-800">
            {/* 빠른 제안 버튼 */}
            <div className="mb-3">
              <div className="flex items-center gap-1.5 mb-2">
                <Lightbulb className="h-3.5 w-3.5 text-amber-500" />
                <span className="text-xs text-gray-500 dark:text-gray-400">빠른 피드백</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {quickSuggestions.map((suggestion) => (
                  <button
                    key={suggestion.text}
                    onClick={() => {
                      setInput(suggestion.text);
                      inputRef.current?.focus();
                    }}
                    disabled={isLoading}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-full bg-gray-100 dark:bg-dark-700 border border-gray-200 dark:border-dark-600 text-gray-700 dark:text-gray-300 hover:border-indigo-300 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span>{suggestion.icon}</span>
                    <span>{suggestion.text}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* 입력 영역 */}
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="피드백을 입력하세요... (예: 2주차가 너무 빡세요)"
                disabled={isLoading}
                className="flex-1 px-4 py-3 rounded-xl border border-gray-200 dark:border-dark-600 bg-gray-50 dark:bg-dark-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:bg-white dark:focus:bg-dark-600 disabled:opacity-50 text-sm transition-all"
              />
              <Button
                type="submit"
                variant="primary"
                disabled={!input.trim() || isLoading}
                className="px-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 border-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>

            {/* 액션 버튼 */}
            <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200 dark:border-dark-600">
              <Button
                variant="ghost"
                onClick={onCancel}
                className="flex-1 rounded-xl hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-400 hover:border-red-200 dark:hover:border-red-500/30"
              >
                <X className="h-4 w-4 mr-2" />
                취소
              </Button>
              <Button
                variant="primary"
                onClick={onFinalize}
                disabled={isLoading}
                className="flex-1 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 border-0"
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                확정하기
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 오른쪽: 로드맵 미리보기 */}
      <div className="flex-1 min-w-0 order-2">
        <div className="h-full bg-white dark:bg-dark-800 rounded-2xl border border-gray-200 dark:border-dark-600 shadow-lg overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-gray-200 dark:border-dark-600 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-500/10 dark:to-orange-500/10">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-500/20">
                <Sparkles className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  로드맵 미리보기
                </h3>
                {roadmapData && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {roadmapData.duration_months}개월 · {roadmapData.monthly_goals.length}개 목표
                  </p>
                )}
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <RoadmapPreview roadmapData={roadmapData} />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 타이핑 인디케이터
 */
function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md">
        <Bot className="h-4 w-4 text-white" />
      </div>
      <div className="bg-white dark:bg-dark-700 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm border border-gray-100 dark:border-dark-600">
        <div className="flex items-center gap-1.5">
          <motion.span
            className="w-2 h-2 rounded-full bg-indigo-500"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
          />
          <motion.span
            className="w-2 h-2 rounded-full bg-indigo-500"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
          />
          <motion.span
            className="w-2 h-2 rounded-full bg-indigo-500"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
          />
        </div>
      </div>
    </motion.div>
  );
}

/**
 * 채팅 메시지 컴포넌트
 */
function ChatMessage({ message }: { message: FeedbackMessage }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className={cn('flex items-start gap-3', isUser ? 'flex-row-reverse' : '')}
    >
      {/* 아바타 */}
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-md',
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-cyan-500'
            : 'bg-gradient-to-br from-indigo-500 to-purple-600'
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>

      {/* 메시지 버블 */}
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3 shadow-sm',
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-cyan-500 text-white rounded-tr-md'
            : 'bg-white dark:bg-dark-700 text-gray-900 dark:text-white border border-gray-100 dark:border-dark-600 rounded-tl-md'
        )}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>

        {/* 수정 내역 표시 */}
        {message.modifications && (
          <ModificationBadge modifications={message.modifications} isUser={isUser} />
        )}
      </div>
    </motion.div>
  );
}

/**
 * 수정 내역 뱃지
 */
function ModificationBadge({
  modifications,
  isUser
}: {
  modifications: RoadmapModifications;
  isUser: boolean;
}) {
  const monthCount = modifications.monthly_goals?.length || 0;
  const weekCount = modifications.weekly_tasks?.length || 0;

  if (monthCount === 0 && weekCount === 0) return null;

  return (
    <div className={cn(
      'mt-2 pt-2 border-t flex items-center gap-1.5 text-xs',
      isUser
        ? 'border-white/20 text-white/80'
        : 'border-gray-200 dark:border-dark-500 text-green-600 dark:text-green-400'
    )}>
      <Edit3 className="h-3 w-3" />
      <span className="font-medium">
        {monthCount > 0 && `${monthCount}개 월 목표`}
        {monthCount > 0 && weekCount > 0 && ', '}
        {weekCount > 0 && `${weekCount}개 주간 과제`}
        {' 수정됨'}
      </span>
    </div>
  );
}

/**
 * 로드맵 미리보기 (접기/펼치기 지원)
 */
function RoadmapPreview({ roadmapData }: { roadmapData: RoadmapPreviewData | null }) {
  const [expandedMonths, setExpandedMonths] = useState<Set<number>>(new Set([1]));

  const toggleMonth = (monthNumber: number) => {
    setExpandedMonths((prev) => {
      const next = new Set(prev);
      if (next.has(monthNumber)) {
        next.delete(monthNumber);
      } else {
        next.add(monthNumber);
      }
      return next;
    });
  };

  if (!roadmapData) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        로드맵 데이터를 불러오는 중...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 제목 카드 */}
      <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-500/10 dark:via-purple-500/10 dark:to-pink-500/10 border border-indigo-200 dark:border-indigo-500/30 rounded-xl p-5">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {roadmapData.title}
        </h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
          {roadmapData.description}
        </p>
        <div className="mt-3 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-white/60 dark:bg-dark-600/60">
            <Calendar className="h-3 w-3" />
            {roadmapData.duration_months}개월
          </span>
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-white/60 dark:bg-dark-600/60">
            📚 {roadmapData.monthly_goals.reduce((acc, g) => {
              const wt = roadmapData.weekly_tasks.find(w => w.month_number === g.month_number);
              return acc + (wt?.weeks.length || 0);
            }, 0)}주 과정
          </span>
        </div>
      </div>

      {/* 월별 카드 (아코디언) */}
      {roadmapData.monthly_goals.map((goal) => {
        const weeklyTasks = roadmapData.weekly_tasks.find(
          (wt) => wt.month_number === goal.month_number
        );
        const isExpanded = expandedMonths.has(goal.month_number);

        // 월별 색상
        const colors = [
          'from-blue-500 to-cyan-500',
          'from-purple-500 to-pink-500',
          'from-amber-500 to-orange-500',
          'from-green-500 to-emerald-500',
          'from-red-500 to-rose-500',
          'from-indigo-500 to-violet-500',
        ];
        const colorClass = colors[(goal.month_number - 1) % colors.length];

        return (
          <div
            key={goal.month_number}
            className="bg-white dark:bg-dark-700 border border-gray-200 dark:border-dark-600 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
          >
            {/* 월 헤더 (클릭하여 토글) */}
            <button
              onClick={() => toggleMonth(goal.month_number)}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-dark-600 transition-colors text-left"
            >
              <div className={cn(
                'w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white font-bold shadow-md',
                colorClass
              )}>
                {goal.month_number}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                  {goal.title}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {goal.month_number}월차 · {weeklyTasks?.weeks.length || 0}주 과정
                </p>
              </div>
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
              </motion.div>
            </button>

            {/* 펼쳐진 내용 */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 pt-2 border-t border-gray-100 dark:border-dark-600">
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                      {goal.description}
                    </p>

                    {/* 주간 과제 */}
                    {weeklyTasks && weeklyTasks.weeks.length > 0 && (
                      <div className="space-y-2">
                        {weeklyTasks.weeks.map((week) => (
                          <div
                            key={week.week_number}
                            className="relative pl-4 py-2.5 bg-gray-50 dark:bg-dark-600/50 rounded-lg border-l-3 border-l-indigo-400"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-xs font-bold">
                                {week.week_number}
                              </span>
                              <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                                {week.title}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 ml-7">
                              {week.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}

export default FeedbackChat;
