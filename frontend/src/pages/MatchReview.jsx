import React, { useEffect, useState } from 'react';
import { GitMerge, Filter, CheckCircle, XCircle, Edit3, ArrowRight, ShieldAlert, Sparkles, RefreshCw, Search } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import ScoreBreakdown from '../components/ScoreBreakdown';
import ClusterDetailModal from '../components/ClusterDetailModal';
import { listMatches, getMatch, approveMatch, editApproveMatch, rejectMatch } from '../api/client';

export default function MatchReview() {
  const [matches, setMatches] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [filterBand, setFilterBand] = useState('');
  const [filterStatus, setFilterStatus] = useState('PENDING');
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchMatches = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterBand) params.confidence_band = filterBand;
      if (filterStatus) params.status = filterStatus;
      const res = await listMatches(params);
      setMatches(res);
      if (res.length > 0) {
        // Keep current selected if valid, else pick first
        const exists = res.find((m) => m.id === selectedId);
        if (!exists) {
          setSelectedId(res[0].id);
        }
      } else {
        setSelectedId(null);
        setSelectedMatch(null);
      }
    } catch (err) {
      console.error('Failed to load matches:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatches();
  }, [filterBand, filterStatus]);

  useEffect(() => {
    if (selectedId) {
      const loadDetail = async () => {
        try {
          setDetailLoading(true);
          const res = await getMatch(selectedId);
          setSelectedMatch(res);
        } catch (err) {
          console.error('Failed to load match detail:', err);
        } finally {
          setDetailLoading(false);
        }
      };
      loadDetail();
    }
  }, [selectedId]);

  const handleApprove = async (id) => {
    try {
      setIsProcessing(true);
      const updated = await approveMatch(id, 'Govt Evaluator / Lead Data Steward');
      setSelectedMatch(updated);
      fetchMatches();
    } catch (err) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEditApprove = async (id, data) => {
    try {
      setIsProcessing(true);
      const updated = await editApproveMatch(id, data);
      setSelectedMatch(updated);
      setIsModalOpen(false);
      fetchMatches();
    } catch (err) {
      alert(`Edit & Approve error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async (id, reviewer, reason) => {
    try {
      setIsProcessing(true);
      const updated = await rejectMatch(id, reviewer, reason);
      setSelectedMatch(updated);
      setIsModalOpen(false);
      fetchMatches();
    } catch (err) {
      alert(`Rejection error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const filteredMatches = matches.filter((m) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      (m.suggested_common_code || '').toLowerCase().includes(term) ||
      (m.suggested_description || '').toLowerCase().includes(term) ||
      (m.category || '').toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white font-['Outfit'] flex items-center space-x-2">
            <GitMerge className="w-5 h-5 text-blue-400" />
            <span>Human Validation & Approval Workflow</span>
          </h2>
          <p className="text-xs text-slate-400">
            Review candidate equivalent materials, inspect multi-signal scoring, and authorize Common National Codes.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Status Filter */}
          <div className="flex items-center bg-slate-900 border border-slate-700/80 rounded-xl p-0.5">
            {['PENDING', 'APPROVED', 'REJECTED', ''].map((st) => (
              <button
                key={st || 'ALL'}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                  filterStatus === st
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {st || 'ALL STATUS'}
              </button>
            ))}
          </div>

          {/* Confidence Band Filter */}
          <select
            value={filterBand}
            onChange={(e) => setFilterBand(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 text-slate-300 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Confidence Bands</option>
            <option value="HIGH">High (&gt;90%)</option>
            <option value="MEDIUM">Medium (60–90%)</option>
            <option value="LOW">Low (&lt;60%)</option>
          </select>

          <button
            onClick={fetchMatches}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 transition-colors"
            title="Refresh candidate clusters"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Split Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Cluster List (4 cols) */}
        <div className="lg:col-span-4 glass-panel rounded-2xl border border-slate-800 overflow-hidden flex flex-col h-[75vh]">
          {/* Search bar */}
          <div className="p-3 border-b border-slate-800 bg-slate-950/40 relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-6 top-5" />
            <input
              type="text"
              placeholder="Search clusters, equipment, codes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* List Content */}
          <div className="overflow-y-auto divide-y divide-slate-800/60 flex-1">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400 flex flex-col items-center space-y-2">
                <RefreshCw className="w-5 h-5 animate-spin text-blue-400" />
                <span>Loading Candidate Clusters...</span>
              </div>
            ) : filteredMatches.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500 space-y-2">
                <span>No candidate clusters found matching filters.</span>
              </div>
            ) : (
              filteredMatches.map((m) => {
                const isSelected = selectedId === m.id;
                return (
                  <div
                    key={m.id}
                    onClick={() => setSelectedId(m.id)}
                    className={`p-3.5 cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-blue-600/15 border-l-4 border-blue-500 text-white'
                        : 'hover:bg-slate-800/40 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[11px] font-mono font-bold text-blue-300 truncate max-w-[170px]">
                        {m.suggested_common_code}
                      </span>
                      <StatusBadge status={m.confidence_band} type="confidence" />
                    </div>

                    <p className="text-xs font-medium line-clamp-2 text-slate-200 mb-2">
                      {m.suggested_description}
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/40">
                      <span className="font-semibold text-slate-300">
                        {m.member_count} CPSE Records
                      </span>
                      <span className="font-bold text-slate-200">
                        {Math.round(m.weighted_score * 100)}% Score
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Deep Inspection & Action Panel (8 cols) */}
        <div className="lg:col-span-8 glass-panel rounded-2xl border border-slate-800 overflow-hidden flex flex-col h-[75vh]">
          {detailLoading ? (
            <div className="flex flex-col items-center justify-center h-full space-y-3">
              <RefreshCw className="w-8 h-8 text-blue-400 animate-spin" />
              <span className="text-xs text-slate-400">Loading Cluster Detail & Signal Breakdown...</span>
            </div>
          ) : !selectedMatch ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-2">
              <GitMerge className="w-12 h-12 stroke-1" />
              <span className="text-sm">Select a candidate cluster from the left panel to review</span>
            </div>
          ) : (
            <div className="flex flex-col h-full overflow-hidden">
              {/* Selected Cluster Header */}
              <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-950/60 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-500/30">
                      {selectedMatch.suggested_common_code}
                    </span>
                    <StatusBadge status={selectedMatch.confidence_band} type="confidence" />
                    <StatusBadge status={selectedMatch.status} />
                  </div>
                  <h3 className="text-sm font-bold text-white line-clamp-1">
                    {selectedMatch.suggested_description}
                  </h3>
                </div>

                {/* Quick Actions in Header */}
                {selectedMatch.status === 'PENDING' && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleApprove(selectedMatch.id)}
                      disabled={isProcessing}
                      className="flex items-center space-x-1.5 px-4 py-1.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-md shadow-emerald-600/20 active:scale-95 transition-all"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Approve</span>
                    </button>
                    <button
                      onClick={() => setIsModalOpen(true)}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                    >
                      More Actions
                    </button>
                  </div>
                )}
              </div>

              {/* Scrollable Detail Body */}
              <div className="p-5 overflow-y-auto space-y-6 flex-1">
                {/* Score Breakdown Widget */}
                <ScoreBreakdown
                  semantic={selectedMatch.semantic_score || 0}
                  fuzzy={selectedMatch.fuzzy_score || 0}
                  attribute={selectedMatch.attribute_score || 0}
                  weighted={selectedMatch.weighted_score || 0}
                  band={selectedMatch.confidence_band}
                />

                {/* Constituent CPSE Table */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Constituent CPSE Master Items ({selectedMatch.members?.length || 0})
                    </h4>
                    <span className="text-[10px] text-slate-500">
                      Preserving exact legacy codes for reverse-traceability
                    </span>
                  </div>

                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 font-semibold text-[11px]">
                          <th className="py-2.5 px-3">CPSE / ERP</th>
                          <th className="py-2.5 px-3">Original Code</th>
                          <th className="py-2.5 px-3">Description</th>
                          <th className="py-2.5 px-3">Unit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {selectedMatch.members?.map((m) => (
                          <tr key={m.id} className="hover:bg-slate-800/30 transition-colors">
                            <td className="py-2.5 px-3">
                              <span className="inline-block px-1.5 py-0.5 rounded bg-slate-800 text-blue-400 font-mono text-[10px] font-bold">
                                {m.cpse_code}
                              </span>
                              <span className="text-[10px] text-slate-500 block">{m.erp_system}</span>
                            </td>
                            <td className="py-2.5 px-3 font-mono font-bold text-amber-300 select-all">
                              {m.original_code}
                            </td>
                            <td className="py-2.5 px-3 text-slate-200">
                              <div>{m.raw_description}</div>
                              {m.raw_specification && (
                                <span className="text-[10px] text-slate-400 block">{m.raw_specification}</span>
                              )}
                            </td>
                            <td className="py-2.5 px-3 font-semibold text-slate-400 uppercase">
                              {m.unit_of_measure}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Deep Inspection & Edit Modal */}
      {selectedMatch && (
        <ClusterDetailModal
          match={selectedMatch}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onApprove={handleApprove}
          onEditApprove={handleEditApprove}
          onReject={handleReject}
          isProcessing={isProcessing}
        />
      )}
    </div>
  );
}
