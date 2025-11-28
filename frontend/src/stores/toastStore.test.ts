import { describe, it, expect, beforeEach } from 'vitest';
import { useToastStore, toast } from './toastStore';
import { act } from '@testing-library/react';

describe('toastStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useToastStore.setState({ toasts: [] });
  });

  describe('addToast', () => {
    it('adds a toast to the store', () => {
      act(() => {
        useToastStore.getState().addToast({
          type: 'success',
          message: 'Test message',
        });
      });

      const { toasts } = useToastStore.getState();
      expect(toasts).toHaveLength(1);
      expect(toasts[0].message).toBe('Test message');
      expect(toasts[0].type).toBe('success');
    });

    it('assigns unique id to each toast', () => {
      act(() => {
        useToastStore.getState().addToast({ type: 'success', message: 'First' });
        useToastStore.getState().addToast({ type: 'error', message: 'Second' });
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].id).not.toBe(toasts[1].id);
    });
  });

  describe('removeToast', () => {
    it('removes a toast by id', () => {
      act(() => {
        useToastStore.getState().addToast({ type: 'success', message: 'Test' });
      });

      const { toasts } = useToastStore.getState();
      const toastId = toasts[0].id;

      act(() => {
        useToastStore.getState().removeToast(toastId);
      });

      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('does nothing for non-existent id', () => {
      act(() => {
        useToastStore.getState().addToast({ type: 'success', message: 'Test' });
        useToastStore.getState().removeToast('non-existent');
      });

      expect(useToastStore.getState().toasts).toHaveLength(1);
    });
  });

  describe('helper methods', () => {
    it('success() adds success toast', () => {
      act(() => {
        useToastStore.getState().success('Success!');
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('success');
      expect(toasts[0].message).toBe('Success!');
    });

    it('error() adds error toast', () => {
      act(() => {
        useToastStore.getState().error('Error!');
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('error');
    });

    it('warning() adds warning toast', () => {
      act(() => {
        useToastStore.getState().warning('Warning!');
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('warning');
    });

    it('info() adds info toast', () => {
      act(() => {
        useToastStore.getState().info('Info!');
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('info');
    });
  });

  describe('toast helper object', () => {
    it('works outside of React components', () => {
      act(() => {
        toast.success('Success message');
      });

      const { toasts } = useToastStore.getState();
      expect(toasts[0].type).toBe('success');
    });
  });
});
