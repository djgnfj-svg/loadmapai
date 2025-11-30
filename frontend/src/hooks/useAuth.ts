import { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import type { User } from '@/types';

export function useLogin() {
  const navigate = useNavigate();
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (response) => {
      const { user, access_token } = response.data;
      login(user, access_token);
      navigate('/roadmaps');
    },
  });
}

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      navigate('/login');
    },
  });
}

export function useCurrentUser() {
  const { setUser, setLoading, token } = useAuthStore();

  const query = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await authApi.me();
      return response.data as User;
    },
    enabled: !!token,
  });

  useEffect(() => {
    if (query.isSuccess && query.data) {
      setUser(query.data);
      setLoading(false);
    }
    if (query.isError) {
      setUser(null);
      setLoading(false);
    }
  }, [query.isSuccess, query.isError, query.data, setUser, setLoading]);

  return query;
}

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  return () => {
    logout();
    queryClient.clear();
    navigate('/');
  };
}
