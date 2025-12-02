import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from '@/components/layout';
import { ErrorBoundary, ToastContainer } from '@/components/common';
import {
  Home,
  Login,
  Register,
  Dashboard,
  RoadmapCreate,
  RoadmapList,
  RoadmapDetail,
  NotFound,
  Settings,
} from '@/pages';
import { useAuthStore } from '@/stores/authStore';
import { useToastStore } from '@/stores/toastStore';
import { useThemeStore } from '@/stores/themeStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}

function ThemeInitializer() {
  const { theme, setTheme } = useThemeStore();

  useEffect(() => {
    setTheme(theme);
  }, []);

  return null;
}

function App() {
  const { toasts, removeToast } = useToastStore();

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeInitializer />
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<PublicRoute><Home /></PublicRoute>} />
              <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmaps"
                element={
                  <ProtectedRoute>
                    <RoadmapList />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmaps/create"
                element={
                  <ProtectedRoute>
                    <RoadmapCreate />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/roadmaps/:id"
                element={
                  <ProtectedRoute>
                    <RoadmapDetail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
          <ToastContainer toasts={toasts} onClose={removeToast} />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
