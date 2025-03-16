
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/toaster';
import QueryProvider from '@/providers/QueryProvider';
import { NotificationProvider } from '@/contexts/NotificationContext';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Index from '@/pages/Index';
import CreateCampaign from '@/pages/CreateCampaign';
import Create from '@/pages/Create';
import Platforms from '@/pages/Platforms';
import Analytics from '@/pages/Analytics';
import CampaignAnalytics from '@/pages/CampaignAnalytics';
import NotFound from '@/pages/NotFound';
import CampaignDetails from './pages/CampaignDetails';
import EditCampaign from './pages/EditCampaign';
import './App.css';

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="adflux-theme">
      <QueryProvider>
        <NotificationProvider>
          <Router>
            <div className="flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">
                <Routes>
                  <Route path="/" element={<Index />} />
                  <Route path="/create-campaign" element={<CreateCampaign />} />
                  <Route path="/create" element={<Create />} />
                  <Route path="/platforms" element={<Platforms />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/analytics/campaign/:id" element={<CampaignAnalytics />} />
                  <Route path="/campaign/:id" element={<CampaignDetails />} />
                  <Route path="/campaign/:id/edit" element={<EditCampaign />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </Router>
        </NotificationProvider>
      </QueryProvider>
      <Toaster />
    </ThemeProvider>
  );
}

export default App;
