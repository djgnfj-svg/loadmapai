import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Sparkles, Calendar, Brain, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Home() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="relative">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 dark:bg-primary-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 dark:bg-accent-500/5 rounded-full blur-3xl" />
      </div>

      {/* Hero section */}
      <div className="text-center py-16 md:py-24">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400 text-sm font-medium mb-6">
          <Sparkles className="w-4 h-4" />
          AI 기반 학습 로드맵 생성기
        </div>

        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
          AI로 만드는<br />
          <span className="bg-gradient-to-r from-primary-600 to-accent-500 dark:from-primary-400 dark:to-accent-400 bg-clip-text text-transparent">
            나만의 학습 로드맵
          </span>
        </h1>

        <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
          학습 주제를 입력하면 AI가 월별, 주별, 일별 학습 계획을 자동으로 생성합니다.
          매일 퀴즈로 학습 내용을 점검하고 피드백을 받아보세요.
        </p>

        {isAuthenticated ? (
          <Link
            to="/roadmaps/create"
            className={cn(
              'inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold rounded-2xl',
              'text-white bg-gradient-to-r from-primary-600 to-primary-500',
              'hover:from-primary-500 hover:to-primary-400',
              'shadow-xl shadow-primary-500/25 hover:shadow-2xl hover:shadow-primary-500/30',
              'transition-all duration-300 hover:-translate-y-1'
            )}
          >
            새 로드맵 만들기
            <ArrowRight className="w-5 h-5" />
          </Link>
        ) : (
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/register"
              className={cn(
                'inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold rounded-2xl',
                'text-white bg-gradient-to-r from-primary-600 to-primary-500',
                'hover:from-primary-500 hover:to-primary-400',
                'shadow-xl shadow-primary-500/25 hover:shadow-2xl hover:shadow-primary-500/30',
                'transition-all duration-300 hover:-translate-y-1'
              )}
            >
              무료로 시작하기
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className={cn(
                'inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold rounded-2xl',
                'text-primary-600 dark:text-primary-400',
                'bg-white dark:bg-dark-800',
                'border-2 border-primary-200 dark:border-primary-500/30',
                'hover:border-primary-500 dark:hover:border-primary-400',
                'hover:bg-primary-50 dark:hover:bg-primary-500/10',
                'transition-all duration-300'
              )}
            >
              로그인
            </Link>
          </div>
        )}
      </div>

      {/* Features section */}
      <div className="py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <FeatureCard
            icon={<Sparkles className="w-6 h-6" />}
            title="AI 로드맵 생성"
            description="학습 주제와 기간을 입력하면 AI가 체계적인 학습 계획을 생성합니다."
            gradient="from-primary-500 to-primary-600"
          />
          <FeatureCard
            icon={<Calendar className="w-6 h-6" />}
            title="일일 학습 관리"
            description="월별 → 주별 → 일별로 세분화된 태스크를 체크하며 진행하세요."
            gradient="from-secondary-500 to-secondary-600"
          />
          <FeatureCard
            icon={<Brain className="w-6 h-6" />}
            title="학습 퀴즈"
            description="매일 학습한 내용을 퀴즈로 점검하고 AI 피드백을 받아보세요."
            gradient="from-accent-500 to-accent-600"
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  gradient,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
}) {
  return (
    <div className={cn(
      'group relative p-6 rounded-2xl transition-all duration-300',
      'bg-white dark:bg-dark-800',
      'border border-gray-100 dark:border-dark-700',
      'hover:shadow-xl hover:shadow-gray-200/50 dark:hover:shadow-dark-900/50',
      'hover:-translate-y-1'
    )}>
      <div className={cn(
        'inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4',
        'text-white',
        `bg-gradient-to-br ${gradient}`
      )}>
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
        {description}
      </p>
    </div>
  );
}
