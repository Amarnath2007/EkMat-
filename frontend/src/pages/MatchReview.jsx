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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-xl font-bold text-slate-900 font-['Outfit'] flex items-center space-x-2">
            <GitMerge className="w-5 h-5 text-blue-600" />
            <span>Human Validation & Approval Workflow</span>
          </h2>
          <p className="text-xs text-slate-500">
            Review candidate equivalent materials, inspect multi-signal scoring, and authorize Common National Codes.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Status Filter */}
          <div className="flex items-center bg-slate-100 border border-slate-200 rounded-xl p-0.5">
            {['PENDING', 'APPROVED', 'REJECTED', ''].map((st) => (
              <button
                key={st || 'ALL'}
                onClick={() => setFilterStatus(st)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                  filterStatus === st
                    ? 'bg-white text-blue-700 shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
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
            className="bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="">All Confidence Bands</option>
            <option value="HIGH">High (&gt;90%)</option>
            <option value="MEDIUM">Medium (60–90%)</option>
            <option value="LOW">Low (&lt;60%)</option>
          </select>

          <button
            onClick={fetchMatches}
            className="p-2 rounded-xl bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200 transition-colors shadow-xs"
            title="Refresh candidate clusters"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Split Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Cluster List (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col h-[75vh]">
          {/* Search bar */}
          <div className="p-3 border-b border-slate-200 bg-slate-50 relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-6 top-5" />
            <input
              type="text"
              placeholder="Search clusters, equipment, codes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-xs"
            />
          </div>

          {/* List Content */}
          <div className="overflow-y-auto divide-y divide-slate-100 flex-1">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-500 flex flex-col items-center space-y-2">
                <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
                <span>Loading Candidate Clusters...</span>
              </div>
            ) : filteredMatches.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400 space-y-2">
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
                        ? 'bg-blue-50/80 border-l-4 border-blue-600 text-slate-900'
                        : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[11px] font-mono font-bold text-blue-700 truncate max-w-[170px]">
                        {m.suggested_common_code}
                      </span>
                      <StatusBadge status={m.confidence_band} type="confidence" />
                    </div>

                    <p className="text-xs font-semibold line-clamp-2 text-slate-800 mb-2">
                      {m.suggested_description}
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1.5 border-t border-slate-100">
                      <span className="font-semibold text-slate-600">
                        {m.member_count} CPSE Records
                      </span>
                      <span className="font-bold text-slate-800">
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
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden flex flex-col h-[75vh]">
          {detailLoading ? (
            <div className="flex flex-col items-center justify-center h-full space-y-3">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
              <span className="text-xs text-slate-500">Loading Cluster Detail & Signal Breakdown...</span>
            </div>
          ) : !selectedMatch ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
              <GitMerge className="w-12 h-12 stroke-1" />
              <span className="text-sm">Select a candidate cluster from the left panel to review</span>
            </div>
          ) : (
            <div className="flex flex-col h-full overflow-hidden">
              {/* Selected Cluster Header */}
              <div className="p-4 sm:p-5 border-b border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="flex items-center space-x-2 mb-1.5">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {selectedMatch.suggested_common_code}
                    </span>
                    <StatusBadge status={selectedMatch.confidence_band} type="confidence" />
                    <StatusBadge status={selectedMatch.status} />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 line-clamp-1">
                    {selectedMatch.suggested_description}
                  </h3>
                </div>

                {/* Quick Actions in Header */}
                {selectedMatch.status === 'PENDING' && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleApprove(selectedMatch.id)}
                      disabled={isProcessing}
                      className="flex items-center space-x-1.5 px-4 py-1.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-sm shadow-emerald-500/20 active:scale-95 transition-all"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Approve</span>
                    </button>
                    <button
                      onClick={() => setIsModalOpen(true)}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition-colors shadow-xs"
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
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                      Constituent CPSE Master Items ({selectedMatch.members?.length || 0})
                    </h4>
                    <span className="text-[10px] text-slate-500">
                      Preserving exact legacy codes for reverse-traceability
                    </span>
                  </div>

                  <div className="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-xs">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold text-[11px]">
                          <th className="py-2.5 px-3">CPSE / ERP</th>
                          <th className="py-2.5 px-3">Original Code</th>
                          <th className="py-2.5 px-3">Description</th>
                          <th className="py-2.5 px-3">Unit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {selectedMatch.members?.map((m) => (
                          <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                            <td className="py-2.5 px-3">
                              <span className="inline-block px-1.5 py-0.5 rounded bg-slate-100 text-blue-700 font-mono text-[10px] font-bold">
                                {m.cpse_code}
                              </span>
                              <span className="text-[10px] text-slate-500 block font-medium">{m.erp_system}</span>
                            </td>
                            <td className="py-2.5 px-3 font-mono font-bold text-amber-800 select-all">
                              {m.original_code}
                            </td>
                            <td className="py-2.5 px-3 text-slate-800">
                              <div className="font-medium">{m.raw_description}</div>
                              {m.raw_specification && (
                                <span className="text-[10px] text-slate-500 block">{m.raw_specification}</span>
                              )}
                            </td>
                            <td className="py-2.5 px-3 font-semibold text-slate-600 uppercase">
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
