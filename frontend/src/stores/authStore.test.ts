import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from './authStore';
import { act } from '@testing-library/react';

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    vi.clearAllMocks();
  });

  describe('login', () => {
    it('sets user and token', () => {
      const user = { id: '1', email: 'test@example.com', name: 'Test User' };
      const token = 'test-token';

      act(() => {
        useAuthStore.getState().login(user, token);
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(user);
      expect(state.token).toBe(token);
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe('logout', () => {
    it('clears user and token', () => {
      // First login
      act(() => {
        useAuthStore.getState().login(
          { id: '1', email: 'test@example.com', name: 'Test' },
          'test-token'
        );
      });

      // Then logout
      act(() => {
        useAuthStore.getState().logout();
      });

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe('setUser', () => {
    it('updates user without changing token', () => {
      const initialUser = { id: '1', email: 'test@example.com', name: 'Test' };
      const updatedUser = { id: '1', email: 'test@example.com', name: 'Updated' };

      act(() => {
        useAuthStore.getState().login(initialUser, 'test-token');
        useAuthStore.getState().setUser(updatedUser);
      });

      const state = useAuthStore.getState();
      expect(state.user?.name).toBe('Updated');
      expect(state.token).toBe('test-token');
    });
  });

  describe('setToken', () => {
    it('updates token without changing user', () => {
      const user = { id: '1', email: 'test@example.com', name: 'Test' };

      act(() => {
        useAuthStore.getState().login(user, 'old-token');
        useAuthStore.getState().setToken('new-token');
      });

      const state = useAuthStore.getState();
      expect(state.token).toBe('new-token');
      expect(state.user).toEqual(user);
    });
  });

  describe('setLoading', () => {
    it('updates loading state', () => {
      act(() => {
        useAuthStore.getState().setLoading(true);
      });

      expect(useAuthStore.getState().isLoading).toBe(true);

      act(() => {
        useAuthStore.getState().setLoading(false);
      });

      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });
});
