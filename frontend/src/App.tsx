import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';

import { DashboardPage } from './pages/DashboardPage';
import { StockWorkspacePage } from './pages/StockWorkspacePage';
import { AssistantPage } from './pages/AssistantPage';
import { ResearchAgentPage } from './pages/ResearchAgentPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { RAGExplorerPage } from './pages/RAGExplorerPage';
import { SentimentPage } from './pages/SentimentPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { AnalyticsLabPage } from './pages/AnalyticsLabPage';
import { MLLabPage } from './pages/MLLabPage';
import { MultimodalPage } from './pages/MultimodalPage';
import { VoicePage } from './pages/VoicePage';
import { ShowcasePage } from './pages/ShowcasePage';
import { SettingsPage } from './pages/SettingsPage';
import { WorkflowPage } from './pages/WorkflowPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
});

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app-container">
          <Sidebar />

          <div className="main-content">
            <Navbar theme={theme} onToggleTheme={toggleTheme} />

            <main style={{ flex: 1 }}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/stocks" element={<StockWorkspacePage />} />
                <Route path="/stocks/:ticker" element={<StockWorkspacePage />} />
                <Route path="/assistant" element={<AssistantPage />} />
                <Route path="/research-agent" element={<ResearchAgentPage />} />
                <Route path="/workflow" element={<WorkflowPage />} />
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/rag" element={<RAGExplorerPage />} />
                <Route path="/sentiment" element={<SentimentPage />} />
                <Route path="/portfolio" element={<PortfolioPage />} />
                <Route path="/analytics-lab" element={<AnalyticsLabPage />} />
                <Route path="/ml-lab" element={<MLLabPage />} />
                <Route path="/multimodal" element={<MultimodalPage />} />
                <Route path="/voice" element={<VoicePage />} />
                <Route path="/showcase" element={<ShowcasePage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
