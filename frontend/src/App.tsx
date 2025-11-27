import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from '@/components/layout';
import { Home, Login, Register, AuthCallback } from '@/pages';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            {/* TODO: 추가 라우트 */}
            {/* <Route path="/roadmaps" element={<Roadmaps />} /> */}
            {/* <Route path="/roadmaps/new" element={<NewRoadmap />} /> */}
            {/* <Route path="/roadmaps/:id" element={<RoadmapDetail />} /> */}
            {/* <Route path="/learning" element={<Learning />} /> */}
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
