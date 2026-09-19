import React from 'react';
import { Layers, Database, GitMerge, FileText, UploadCloud, Play, CheckCircle2, Shield, Activity } from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  onOpenImport,
  onRunMatching,
  isMatching,
  pendingCount = 0
}) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'matches', label: 'Match Review', icon: GitMerge, badge: pendingCount > 0 ? pendingCount : null },
    { id: 'catalog', label: 'Material Master', icon: Database },
    { id: 'audit', label: 'Audit Trail', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      {/* Tricolor Government Identity Ribbon */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-500 opacity-90"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Emblem */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-blue-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 border border-blue-400/30">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight text-white font-['Outfit']">EkMat</span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-500/30">
                  SIH26099
                </span>
                <span className="hidden md:inline-flex items-center text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 animate-pulse"></span>
                  Team Black Hats
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                CPSE Material Standardization & Harmonization Platform
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all duration-150 relative ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-sm shadow-blue-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge !== null && item.badge !== undefined && (
                    <span className="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-500 text-slate-950">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Quick Action Controls */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <button
              onClick={onOpenImport}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-800/90 text-slate-200 hover:bg-slate-700 border border-slate-700/80 transition-colors shadow-sm"
              title="Upload CPSE Material Master CSV"
            >
              <UploadCloud className="w-3.5 h-3.5 text-blue-400" />
              <span className="hidden sm:inline">Import CSV</span>
            </button>

            <button
              onClick={onRunMatching}
              disabled={isMatching}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold text-white transition-all shadow-md ${
                isMatching
                  ? 'bg-indigo-700/60 cursor-not-allowed opacity-80'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-blue-600/20 active:scale-95'
              }`}
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isMatching ? 'animate-spin text-indigo-200' : ''}`} />
              <span>{isMatching ? 'Matching...' : 'Run Matching'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
