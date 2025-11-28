import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Trophy, Target, TrendingUp, RotateCcw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { quizApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { CircularProgress } from '@/components/common/Progress';
import { LoadingScreen } from '@/components/common/Loading';
import { FeedbackView } from '@/components/quiz/FeedbackView';
import { cn } from '@/lib/utils';
import type { QuizResult as QuizResultType } from '@/types';

export function QuizResult() {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();

  const { data: result, isLoading, error } = useQuery({
    queryKey: ['quiz', quizId, 'result'],
    queryFn: async () => {
      const response = await quizApi.grade(quizId!);
      return response.data as QuizResultType;
    },
    enabled: !!quizId,
  });

  if (isLoading) {
    return <LoadingScreen message="결과를 불러오는 중..." />;
  }

  if (error || !result) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          결과를 찾을 수 없습니다
        </h2>
        <p className="text-gray-500 mb-6">
          퀴즈 결과를 불러오는 중 오류가 발생했습니다.
        </p>
        <Button variant="primary" onClick={() => navigate(-1)}>
          돌아가기
        </Button>
      </div>
    );
  }

  const score = result.score || 0;
  const getScoreColor = () => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'primary';
    if (score >= 50) return 'warning';
    return 'danger';
  };

  const getScoreMessage = () => {
    if (score >= 90) return '훌륭합니다! 완벽에 가까운 성적입니다.';
    if (score >= 70) return '잘 하셨어요! 대부분의 내용을 이해하고 있습니다.';
    if (score >= 50) return '괜찮습니다. 몇 가지 부분만 더 공부하면 됩니다.';
    return '조금 더 복습이 필요해요. 다시 도전해보세요!';
  };

  // Create a map of user answers by question ID
  const userAnswerMap = new Map(
    result.user_answers?.map(ua => [ua.question_id, ua]) || []
  );

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>대시보드로</span>
        </button>
      </div>

      {/* Score Card */}
      <Card variant="bordered">
        <CardContent>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-shrink-0">
              <CircularProgress
                value={score}
                size={160}
                strokeWidth={12}
                color={getScoreColor()}
              />
            </div>

            <div className="flex-1 text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
                <Trophy className={cn(
                  'h-6 w-6',
                  score >= 70 ? 'text-yellow-500' : 'text-gray-400'
                )} />
                <h1 className="text-2xl font-bold text-gray-900">퀴즈 완료!</h1>
              </div>

              <p className="text-lg text-gray-600 mb-4">
                {getScoreMessage()}
              </p>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {result.correct_count}
                  </div>
                  <div className="text-xs text-gray-500">정답</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {result.total_questions - (result.correct_count || 0)}
                  </div>
                  <div className="text-xs text-gray-500">오답</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {result.total_questions}
                  </div>
                  <div className="text-xs text-gray-500">총 문제</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Feedback Summary */}
      {result.feedback_summary && (
        <Card variant="bordered">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary-600" />
              AI 피드백
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{result.feedback_summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Question Results */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary-600" />
          문제별 결과
        </h2>

        <div className="space-y-4">
          {result.questions?.map((question, index) => (
            <FeedbackView
              key={question.id}
              question={question}
              userAnswer={userAnswerMap.get(question.id)}
              questionIndex={index}
            />
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-center gap-4 pt-6 border-t">
        <Link to="/dashboard">
          <Button variant="outline">
            대시보드로 이동
          </Button>
        </Link>
        <Button
          variant="primary"
          onClick={() => navigate(-2)}
        >
          <RotateCcw className="h-4 w-4 mr-1" />
          다시 학습하기
        </Button>
      </div>
    </div>
  );
}
