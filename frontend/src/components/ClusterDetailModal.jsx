import React, { useState } from 'react';
import { X, CheckCircle, Edit3, XCircle, ShieldCheck, Building2, Tag, ArrowRight, Layers, FileCode } from 'lucide-react';
import StatusBadge from './StatusBadge';
import ScoreBreakdown from './ScoreBreakdown';

export default function ClusterDetailModal({
  match,
  isOpen,
  onClose,
  onApprove,
  onEditApprove,
  onReject,
  isProcessing
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedDescription, setEditedDescription] = useState('');
  const [editedCode, setEditedCode] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectPrompt, setShowRejectPrompt] = useState(false);

  if (!isOpen || !match) return null;

  const handleStartEdit = () => {
    setEditedDescription(match.suggested_description || '');
    setEditedCode(match.suggested_common_code || '');
    setIsEditing(true);
    setShowRejectPrompt(false);
  };

  const handleSaveEdit = () => {
    if (!editedDescription.trim()) return;
    onEditApprove(match.id, {
      edited_description: editedDescription,
      edited_common_code: editedCode.trim() || match.suggested_common_code,
      reviewed_by: 'Govt Evaluator / Lead Data Steward'
    });
    setIsEditing(false);
  };

  const handleConfirmReject = () => {
    onReject(match.id, 'Govt Evaluator', rejectReason || 'Technical specification mismatch');
    setShowRejectPrompt(false);
  };

  const members = match.members || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fadeIn">
      <div className="relative w-full max-w-4xl bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg border border-blue-200">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-slate-900 font-['Outfit']">Candidate Cluster #{match.id}</h3>
                <StatusBadge status={match.confidence_band} type="confidence" />
                <StatusBadge status={match.status} />
              </div>
              <p className="text-xs text-slate-500">
                Category: <span className="text-slate-800 font-semibold">{match.category || 'GENERAL'}</span> | Constituent Records: <span className="text-slate-800 font-semibold">{members.length} CPSE Master Items</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Top Grid: Suggested Code & Multi-Signal Score */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Suggested National Code Card */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center">
                    <FileCode className="w-4 h-4 mr-1.5 text-blue-600" />
                    Suggested Common National Code
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                    Auto-Formatted
                  </span>
                </div>
                <div className="font-mono text-base font-bold text-blue-700 bg-slate-50 p-3 rounded-lg border border-slate-200 select-all shadow-xs">
                  {match.suggested_common_code}
                </div>

                <div className="mt-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    Standardized Harmonized Description
                  </span>
                  <div className="text-xs text-slate-800 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed font-medium">
                    {match.suggested_description}
                  </div>
                </div>
              </div>

              {match.reviewed_by && (
                <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex justify-between">
                  <span>Reviewed By: <strong className="text-slate-700">{match.reviewed_by}</strong></span>
                  <span>{match.reviewed_at ? new Date(match.reviewed_at).toLocaleString() : ''}</span>
                </div>
              )}
            </div>

            {/* Score Breakdown Visualizer */}
            <ScoreBreakdown
              semantic={match.semantic_score || 0}
              fuzzy={match.fuzzy_score || 0}
              attribute={match.attribute_score || 0}
              weighted={match.weighted_score || 0}
              band={match.confidence_band}
            />
          </div>

          {/* Edit Form Drawer if active */}
          {isEditing && (
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 space-y-3 animate-fadeIn">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-blue-800 uppercase tracking-wider flex items-center">
                  <Edit3 className="w-3.5 h-3.5 mr-1.5" />
                  Human Steward Edit & Approve
                </h4>
                <button
                  onClick={() => setIsEditing(false)}
                  className="text-xs text-slate-500 hover:text-slate-800"
                >
                  Cancel
                </button>
              </div>
              <div className="space-y-2">
                <label className="text-xs text-slate-700 block font-semibold">Common National Code</label>
                <input
                  type="text"
                  value={editedCode}
                  onChange={(e) => setEditedCode(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-blue-700 font-mono font-bold focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs text-slate-700 block font-semibold">Standardized Description</label>
                <textarea
                  value={editedDescription}
                  onChange={(e) => setEditedDescription(e.target.value)}
                  rows={2}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-medium"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  onClick={handleSaveEdit}
                  disabled={isProcessing}
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-colors shadow-xs"
                >
                  Save & Approve
                </button>
              </div>
            </div>
          )}

          {/* Reject Reason Prompt if active */}
          {showRejectPrompt && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 space-y-3 animate-fadeIn">
              <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider flex items-center">
                <XCircle className="w-3.5 h-3.5 mr-1.5" />
                Provide Rejection Rationale for Governance Audit
              </h4>
              <input
                type="text"
                placeholder="E.g. Incompatible equipment rating or size difference"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="w-full bg-white border border-rose-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-rose-500"
              />
              <div className="flex justify-end space-x-2 pt-1">
                <button
                  onClick={() => setShowRejectPrompt(false)}
                  className="px-3 py-1 text-xs text-slate-500 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmReject}
                  disabled={isProcessing}
                  className="px-4 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold transition-colors shadow-xs"
                >
                  Confirm Rejection
                </button>
              </div>
            </div>
          )}

          {/* Constituent CPSE Records Table */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center">
                <Building2 className="w-4 h-4 mr-1.5 text-slate-500" />
                Constituent CPSE Master Records ({members.length})
              </h4>
              <span className="text-[11px] text-slate-500">
                Preserving original ERP codes for 100% backward traceability
              </span>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-xl bg-white shadow-xs">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold">
                    <th className="py-2.5 px-3">CPSE Entity</th>
                    <th className="py-2.5 px-3">Original Material Code</th>
                    <th className="py-2.5 px-4">Raw Description (Legacy ERP)</th>
                    <th className="py-2.5 px-3">ERP Spec / Units</th>
                    <th className="py-2.5 px-3">Extracted Attributes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {members.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2.5 px-3 font-semibold text-slate-800">
                        <span className="inline-block px-2 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] text-blue-700 font-bold">
                          {m.cpse_code}
                        </span>
                        <span className="text-[10px] text-slate-500 block font-medium">{m.erp_system}</span>
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-amber-800 select-all">
                        {m.original_code}
                      </td>
                      <td className="py-2.5 px-4 text-slate-800 font-medium">
                        {m.raw_description}
                      </td>
                      <td className="py-2.5 px-3 text-slate-600">
                        <div>{m.raw_specification || '—'}</div>
                        <span className="text-[10px] text-slate-500 uppercase">{m.unit_of_measure}</span>
                      </td>
                      <td className="py-2.5 px-3 text-[11px]">
                        {m.extracted_attributes && (
                          <div className="flex flex-wrap gap-1">
                            {m.extracted_attributes.type && (
                              <span className="px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 text-[10px] font-medium">
                                {m.extracted_attributes.type}
                              </span>
                            )}
                            {m.extracted_attributes.size_mm && (
                              <span className="px-1.5 py-0.2 rounded bg-teal-50 text-teal-700 border border-teal-200 text-[10px] font-medium">
                                {m.extracted_attributes.size_mm}
                              </span>
                            )}
                            {m.extracted_attributes.material && (
                              <span className="px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 border border-slate-200 text-[10px]">
                                {m.extracted_attributes.material}
                              </span>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer Human Action Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 bg-slate-50">
          <div className="text-xs text-slate-600">
            {match.status === 'APPROVED' ? (
              <span className="text-emerald-700 font-medium flex items-center">
                <CheckCircle className="w-4 h-4 mr-1.5" />
                This cluster has been finalized into the National Material Master
              </span>
            ) : match.status === 'REJECTED' ? (
              <span className="text-rose-700 font-medium flex items-center">
                <XCircle className="w-4 h-4 mr-1.5" />
                This cluster was rejected as non-equivalent
              </span>
            ) : (
              <span>Human decision required to mutate CPSE material master state.</span>
            )}
          </div>

          {match.status === 'PENDING' && (
            <div className="flex items-center space-x-3">
              <button
                onClick={() => { setShowRejectPrompt(true); setIsEditing(false); }}
                disabled={isProcessing}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 transition-colors shadow-xs"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>

              <button
                onClick={handleStartEdit}
                disabled={isProcessing}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 transition-colors shadow-xs"
              >
                <Edit3 className="w-3.5 h-3.5 text-blue-600" />
                <span>Edit & Approve</span>
              </button>

              <button
                onClick={() => onApprove(match.id)}
                disabled={isProcessing}
                className="flex items-center space-x-2 px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-sm shadow-emerald-500/20 active:scale-95 transition-all"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Approve Harmonization</span>
              </button>
            </div>
          )}

          {match.status !== 'PENDING' && (
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-300 shadow-xs"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
