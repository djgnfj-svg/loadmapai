import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export function Home() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-bold text-gray-900 mb-6">
        AI로 만드는<br />
        <span className="text-primary-600">나만의 학습 로드맵</span>
      </h1>
      <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        학습 주제를 입력하면 AI가 월별, 주별, 일별 학습 계획을 자동으로 생성합니다.
        매일 퀴즈로 학습 내용을 점검하고 피드백을 받아보세요.
      </p>

      {isAuthenticated ? (
        <Link
          to="/roadmaps/new"
          className="inline-flex items-center px-6 py-3 text-lg font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700"
        >
          새 로드맵 만들기
        </Link>
      ) : (
        <div className="flex justify-center gap-4">
          <Link
            to="/register"
            className="inline-flex items-center px-6 py-3 text-lg font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700"
          >
            무료로 시작하기
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center px-6 py-3 text-lg font-medium rounded-lg text-primary-600 bg-white border-2 border-primary-600 hover:bg-primary-50"
          >
            로그인
          </Link>
        </div>
      )}

      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <FeatureCard
          title="AI 로드맵 생성"
          description="학습 주제와 기간을 입력하면 AI가 체계적인 학습 계획을 생성합니다."
        />
        <FeatureCard
          title="일일 학습 관리"
          description="월별 → 주별 → 일별로 세분화된 태스크를 체크하며 진행하세요."
        />
        <FeatureCard
          title="학습 퀴즈"
          description="매일 학습한 내용을 퀴즈로 점검하고 AI 피드백을 받아보세요."
        />
      </div>
    </div>
  );
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
