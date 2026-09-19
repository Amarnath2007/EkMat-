import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import MatchReview from './pages/MatchReview';
import MaterialMaster from './pages/MaterialMaster';
import AuditTrail from './pages/AuditTrail';
import CSVImportModal from './components/CSVImportModal';
import { runMatching, listMatches } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  const checkPendingMatches = async () => {
    try {
      const res = await listMatches({ status: 'PENDING' });
      setPendingCount(res.length);
    } catch (err) {
      console.error('Failed to check pending matches:', err);
    }
  };

  useEffect(() => {
    checkPendingMatches();
  }, [activeTab]);

  const handleRunMatching = async () => {
    try {
      setIsMatching(true);
      const res = await runMatching();
      await checkPendingMatches();
      alert(`AI Entity Resolution Completed!\n\n${res.total_materials} materials evaluated.\n${res.clusters_created} candidate clusters identified for human validation.`);
      if (activeTab === 'overview') {
        setActiveTab('matches');
      }
    } catch (err) {
      alert(`Matching execution error: ${err.message}`);
    } finally {
      setIsMatching(false);
    }
  };

  const handleImportSuccess = () => {
    checkPendingMatches();
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenImport={() => setIsImportOpen(true)}
        onRunMatching={handleRunMatching}
        isMatching={isMatching}
        pendingCount={pendingCount}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {activeTab === 'overview' && (
          <Overview
            onNavigate={(tab) => setActiveTab(tab)}
            onOpenImport={() => setIsImportOpen(true)}
            onRunMatching={handleRunMatching}
            isMatching={isMatching}
          />
        )}
        {activeTab === 'matches' && <MatchReview />}
        {activeTab === 'catalog' && <MaterialMaster />}
        {activeTab === 'audit' && <AuditTrail />}
      </main>

      {/* Government Hackathon Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/70 py-6 mt-12 text-center text-xs text-slate-500 space-y-2">
        <div className="flex items-center justify-center space-x-2 text-slate-400 font-medium">
          <span>Smart India Hackathon 2026 (SIH26099)</span>
          <span>•</span>
          <span className="text-slate-300">Team Black Hats</span>
          <span>•</span>
          <span>Govt AI Standardization & Entity Resolution Architecture</span>
        </div>
        <p className="text-[11px] text-slate-600 max-w-2xl mx-auto">
          Built with FastAPI, SBERT Sentence Transformers, RapidFuzz, PostgreSQL/pgvector, and React Vite.
          Demonstrated on realistic synthetic CPSE master catalogs with verified ground-truth precision & recall.
        </p>
      </footer>

      {/* CSV Import Modal */}
      <CSVImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onImportSuccess={handleImportSuccess}
      />
    </div>
  );
}
