import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from './authStore';
import { act } from '@testing-library/react';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
    vi.clearAllMocks();
  });

  describe('setAuth', () => {
    it('sets user and token', () => {
      const user = { id: '1', email: 'test@example.com', name: 'Test User' };
      const token = 'test-token';

      act(() => {
        useAuthStore.getState().setAuth(user, token);
      });

      const state = useAuthStore.getState();
      expect(state.user).toEqual(user);
      expect(state.token).toBe(token);
      expect(state.isAuthenticated).toBe(true);
    });

    it('stores token in localStorage', () => {
      act(() => {
        useAuthStore.getState().setAuth(
          { id: '1', email: 'test@example.com', name: 'Test' },
          'test-token'
        );
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token');
    });
  });

  describe('logout', () => {
    it('clears user and token', () => {
      // First set auth
      act(() => {
        useAuthStore.getState().setAuth(
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

    it('removes token from localStorage', () => {
      act(() => {
        useAuthStore.getState().logout();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });
  });

  describe('setUser', () => {
    it('updates user without changing token', () => {
      const initialUser = { id: '1', email: 'test@example.com', name: 'Test' };
      const updatedUser = { id: '1', email: 'test@example.com', name: 'Updated' };

      act(() => {
        useAuthStore.getState().setAuth(initialUser, 'test-token');
        useAuthStore.getState().setUser(updatedUser);
      });

      const state = useAuthStore.getState();
      expect(state.user?.name).toBe('Updated');
      expect(state.token).toBe('test-token');
    });
  });
});
