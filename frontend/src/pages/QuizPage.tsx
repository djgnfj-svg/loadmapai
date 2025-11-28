import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Send, Clock, Sparkles } from 'lucide-react';
import { useQuiz, useQuizForDailyTask, useStartQuiz, useSubmitQuiz, useGradeQuiz, useGenerateQuiz } from '@/hooks/useQuiz';
import { Card, CardContent } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { LoadingScreen } from '@/components/common/Loading';
import { QuestionView, QuizNavigation } from '@/components/quiz';
import type { SubmitAnswerRequest } from '@/types';

export function QuizPage() {
  // taskId is the daily_task_id passed from the roadmap
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();

  // First, try to get existing quiz for this task
  const { data: existingQuiz, isLoading: isLoadingTask, error: taskError } = useQuizForDailyTask(taskId || '');

  // If we have a quiz ID, fetch the full quiz with questions
  const quizId = existingQuiz?.id;
  const { data: quiz, isLoading: isLoadingQuiz, error: quizError } = useQuiz(quizId || '');

  const startQuiz = useStartQuiz();
  const submitQuiz = useSubmitQuiz();
  const gradeQuiz = useGradeQuiz();
  const generateQuiz = useGenerateQuiz();

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<SubmitAnswerRequest[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Initialize answers when quiz loads
  useEffect(() => {
    if (quiz?.questions) {
      setAnswers(
        quiz.questions.map(() => ({ answer_text: '', selected_option: '' }))
      );
    }
  }, [quiz]);

  // Start quiz if pending
  useEffect(() => {
    if (quiz && quiz.status === 'pending' && quizId) {
      startQuiz.mutate(quizId);
    }
  }, [quiz, quizId]);

  const isLoading = isLoadingTask || (quizId && isLoadingQuiz);

  // Handle generating new quiz when none exists
  const handleGenerateQuiz = async () => {
    if (!taskId) return;

    setIsGenerating(true);
    try {
      await generateQuiz.mutateAsync({ dailyTaskId: taskId, numQuestions: 5 });
      // The query will automatically refetch
    } catch (error) {
      console.error('Failed to generate quiz:', error);
      alert('퀴즈 생성에 실패했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return <LoadingScreen message="퀴즈를 불러오는 중..." />;
  }

  // No quiz exists for this task - offer to generate
  if (taskError || (!existingQuiz && !isLoadingTask)) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <div className="bg-white dark:bg-dark-800 rounded-2xl p-8 shadow-lg">
          <div className="w-16 h-16 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            퀴즈 준비하기
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            이 학습 내용에 대한 퀴즈가 아직 없습니다.<br />
            AI가 맞춤형 퀴즈를 생성해드릴까요?
          </p>
          <div className="flex gap-3 justify-center">
            <Button variant="outline" onClick={() => navigate(-1)}>
              돌아가기
            </Button>
            <Button
              variant="primary"
              onClick={handleGenerateQuiz}
              isLoading={isGenerating}
            >
              <Sparkles className="h-4 w-4 mr-1" />
              퀴즈 생성
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (quizError || !quiz) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          퀴즈를 불러올 수 없습니다
        </h2>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          잠시 후 다시 시도해주세요.
        </p>
        <Button variant="primary" onClick={() => navigate(-1)}>
          돌아가기
        </Button>
      </div>
    );
  }

  const questions = quiz.questions || [];
  const currentQuestion = questions[currentQuestionIndex];
  const answeredCount = answers.filter(a => a.answer_text || a.selected_option).length;
  const canSubmit = answeredCount === questions.length;

  const handleAnswerChange = (answer: SubmitAnswerRequest) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestionIndex] = answer;
    setAnswers(newAnswers);
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit) {
      alert('모든 문제에 답변해주세요.');
      return;
    }

    if (!window.confirm('퀴즈를 제출하시겠습니까? 제출 후에는 수정할 수 없습니다.')) {
      return;
    }

    setIsSubmitting(true);
    try {
      // Submit answers
      await submitQuiz.mutateAsync({ quizId: quizId!, answers });

      // Grade quiz
      await gradeQuiz.mutateAsync(quizId!);

      // Navigate to result page
      navigate(`/quiz/${taskId}/result`);
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      alert('퀴즈 제출 중 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>나가기</span>
        </button>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Clock className="h-4 w-4" />
            <span>{answeredCount} / {questions.length} 답변 완료</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Question Navigation - Sidebar */}
        <div className="lg:col-span-1 order-2 lg:order-1">
          <Card variant="bordered">
            <CardContent>
              <QuizNavigation
                questions={questions}
                answers={answers}
                currentIndex={currentQuestionIndex}
                onNavigate={setCurrentQuestionIndex}
              />
            </CardContent>
          </Card>
        </div>

        {/* Question View - Main */}
        <div className="lg:col-span-3 order-1 lg:order-2">
          <Card variant="bordered">
            <CardContent>
              {currentQuestion && (
                <QuestionView
                  question={currentQuestion}
                  questionIndex={currentQuestionIndex}
                  totalQuestions={questions.length}
                  answer={answers[currentQuestionIndex] || {}}
                  onAnswerChange={handleAnswerChange}
                  isSubmitted={quiz.status === 'completed' || quiz.status === 'graded'}
                />
              )}
            </CardContent>
          </Card>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-6">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              이전
            </Button>

            <div className="flex gap-2">
              {currentQuestionIndex === questions.length - 1 ? (
                <Button
                  variant="primary"
                  onClick={handleSubmit}
                  disabled={!canSubmit || isSubmitting}
                  isLoading={isSubmitting}
                >
                  <Send className="h-4 w-4 mr-1" />
                  제출하기
                </Button>
              ) : (
                <Button variant="primary" onClick={handleNext}>
                  다음
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
