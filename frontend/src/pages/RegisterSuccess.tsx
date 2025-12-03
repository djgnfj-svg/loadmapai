import { useState } from 'react';
import { useLocation, Link, Navigate } from 'react-router-dom';
import { Mail, RefreshCw } from 'lucide-react';
import { authApi } from '@/lib/api';
import { cn } from '@/lib/utils';

export function RegisterSuccess() {
  const location = useLocation();
  const email = location.state?.email || '';
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [resendSuccess, setResendSuccess] = useState<boolean | null>(null);

  // 이메일 없이 직접 접근한 경우 회원가입 페이지로 리다이렉트
  if (!email) {
    return <Navigate to="/register" replace />;
  }

  const handleResend = async () => {
    if (isResending) return;

    setIsResending(true);
    setResendMessage('');
    setResendSuccess(null);

    try {
      const response = await authApi.resendVerification(email);
      setResendMessage(response.data.message);
      setResendSuccess(response.data.success);
    } catch {
      setResendMessage('이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요.');
      setResendSuccess(false);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className={cn(
        'w-full max-w-md p-8 rounded-2xl text-center',
        'bg-white dark:bg-dark-800',
        'border border-gray-100 dark:border-dark-700',
        'shadow-xl'
      )}>
        <div className="w-16 h-16 mx-auto bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
          <Mail className="w-8 h-8 text-primary-600 dark:text-primary-400" />
        </div>

        <h2 className="mt-6 text-2xl font-bold text-gray-900 dark:text-white">
          이메일을 확인해주세요
        </h2>

        <p className="mt-4 text-gray-600 dark:text-gray-400">
          <span className="font-medium text-gray-900 dark:text-white">{email}</span>
          <br />
          로 인증 이메일을 발송했습니다.
        </p>

        <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
          이메일의 인증 링크를 클릭하여 회원가입을 완료해주세요.
        </p>

        <div className="mt-8 p-4 bg-gray-50 dark:bg-dark-700 rounded-xl">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            이메일이 도착하지 않았나요?
          </p>
          <ul className="mt-2 text-xs text-gray-500 dark:text-gray-500 text-left list-disc list-inside space-y-1">
            <li>스팸 메일함을 확인해주세요</li>
            <li>이메일 주소가 올바른지 확인해주세요</li>
            <li>몇 분 정도 기다려주세요</li>
          </ul>
        </div>

        <div className="mt-6 space-y-3">
          <button
            onClick={handleResend}
            disabled={isResending}
            className={cn(
              'w-full py-3 rounded-xl font-medium flex items-center justify-center gap-2',
              'border border-gray-200 dark:border-dark-600',
              'text-gray-700 dark:text-gray-300',
              'hover:bg-gray-50 dark:hover:bg-dark-700',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-all duration-200'
            )}
          >
            <RefreshCw className={cn('w-4 h-4', isResending && 'animate-spin')} />
            {isResending ? '발송 중...' : '인증 이메일 재발송'}
          </button>

          <Link
            to="/login"
            className={cn(
              'block w-full py-3 rounded-xl font-medium',
              'text-primary-600 dark:text-primary-400',
              'hover:bg-primary-50 dark:hover:bg-primary-900/20',
              'transition-all duration-200'
            )}
          >
            로그인 페이지로
          </Link>
        </div>

        {resendMessage && (
          <p className={cn(
            'mt-4 text-sm',
            resendSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          )}>
            {resendMessage}
          </p>
        )}
      </div>
    </div>
  );
}
