import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { authApi } from '@/lib/api';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

type VerificationStatus = 'loading' | 'success' | 'error';

export function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<VerificationStatus>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('유효하지 않은 인증 링크입니다.');
      return;
    }

    authApi.verifyEmail(token)
      .then((response) => {
        setStatus('success');
        setMessage(response.data.message);
      })
      .catch((err) => {
        setStatus('error');
        setMessage(err.response?.data?.detail || '인증에 실패했습니다.');
      });
  }, [token]);

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className={cn(
        'w-full max-w-md p-8 rounded-2xl text-center',
        'bg-white dark:bg-dark-800',
        'border border-gray-100 dark:border-dark-700',
        'shadow-xl'
      )}>
        {status === 'loading' && (
          <>
            <Loader2 className="w-16 h-16 mx-auto text-primary-500 animate-spin" />
            <h2 className="mt-6 text-xl font-semibold text-gray-900 dark:text-white">
              인증 중...
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              잠시만 기다려주세요.
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 mx-auto bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
            <h2 className="mt-6 text-xl font-semibold text-gray-900 dark:text-white">
              이메일 인증 완료!
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {message}
            </p>
            <p className="mt-1 text-gray-600 dark:text-gray-400">
              이제 로그인하여 서비스를 이용하실 수 있습니다.
            </p>
            <Link
              to="/login"
              className={cn(
                'inline-block mt-8 px-8 py-3 rounded-xl font-semibold text-white',
                'bg-gradient-to-r from-primary-600 to-primary-500',
                'hover:from-primary-500 hover:to-primary-400',
                'transition-all duration-200'
              )}
            >
              로그인하기
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 mx-auto bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
              <XCircle className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="mt-6 text-xl font-semibold text-gray-900 dark:text-white">
              인증 실패
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {message}
            </p>
            <div className="mt-8 space-y-3">
              <Link
                to="/login"
                className={cn(
                  'block w-full py-3 rounded-xl font-medium',
                  'text-primary-600 dark:text-primary-400',
                  'border border-primary-600 dark:border-primary-400',
                  'hover:bg-primary-50 dark:hover:bg-primary-900/20',
                  'transition-all duration-200'
                )}
              >
                로그인 페이지로
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
