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
    <header className="sticky top-0 z-40 w-full bg-white/95 border-b border-slate-200 shadow-xs backdrop-blur-md">
      {/* Subtle Government Identity Ribbon */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-slate-100 to-emerald-600"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Emblem */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 border border-blue-500">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight text-slate-900 font-['Outfit']">EkMat</span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                  National Portal
                </span>
                <span className="hidden md:inline-flex items-center text-[10px] font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                  CPSE Master Data
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Central Public Sector Enterprises Material Standardization Platform
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
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all duration-150 relative ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border border-blue-200 font-semibold shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                  {item.badge !== null && item.badge !== undefined && (
                    <span className="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-500 text-white shadow-xs">
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
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-white text-slate-700 hover:bg-slate-50 hover:text-slate-900 border border-slate-300 transition-colors shadow-xs"
              title="Upload CPSE Material Master CSV"
            >
              <UploadCloud className="w-3.5 h-3.5 text-blue-600" />
              <span className="hidden sm:inline">Import CSV</span>
            </button>

            <button
              onClick={onRunMatching}
              disabled={isMatching}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold text-white transition-all shadow-sm ${
                isMatching
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-blue-500/20 active:scale-95'
              }`}
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isMatching ? 'animate-spin text-white' : ''}`} />
              <span>{isMatching ? 'Matching...' : 'Run Matching'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
