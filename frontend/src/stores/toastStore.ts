import { create } from 'zustand';
import type { ToastType } from '@/components/common/Toast';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

let toastId = 0;

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = String(++toastId);
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },

  success: (message, duration) => {
    const id = String(++toastId);
    set((state) => ({
      toasts: [...state.toasts, { id, type: 'success', message, duration }],
    }));
  },

  error: (message, duration) => {
    const id = String(++toastId);
    set((state) => ({
      toasts: [...state.toasts, { id, type: 'error', message, duration }],
    }));
  },

  warning: (message, duration) => {
    const id = String(++toastId);
    set((state) => ({
      toasts: [...state.toasts, { id, type: 'warning', message, duration }],
    }));
  },

  info: (message, duration) => {
    const id = String(++toastId);
    set((state) => ({
      toasts: [...state.toasts, { id, type: 'info', message, duration }],
    }));
  },
}));

// Helper function for use outside of React components
export const toast = {
  success: (message: string, duration?: number) =>
    useToastStore.getState().success(message, duration),
  error: (message: string, duration?: number) =>
    useToastStore.getState().error(message, duration),
  warning: (message: string, duration?: number) =>
    useToastStore.getState().warning(message, duration),
  info: (message: string, duration?: number) =>
    useToastStore.getState().info(message, duration),
};
