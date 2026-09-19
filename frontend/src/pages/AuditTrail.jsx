import React, { useEffect, useState } from 'react';
import { FileText, Filter, RefreshCw, UserCheck, Clock, ShieldCheck, ChevronDown, ChevronRight } from 'lucide-react';
import { getAuditTrail } from '../api/client';

export default function AuditTrail() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {};
      if (actionFilter) params.action = actionFilter;
      const res = await getAuditTrail(params);
      setLogs(res);
    } catch (err) {
      console.error('Failed to load audit trail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getActionBadge = (action) => {
    switch (action) {
      case 'APPROVE':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">APPROVE</span>;
      case 'EDIT_APPROVE':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">EDIT & APPROVE</span>;
      case 'REJECT':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">REJECT</span>;
      case 'IMPORT':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">CSV IMPORT</span>;
      case 'MATCH_GENERATED':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">AI MATCH</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">{action}</span>;
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-xl font-bold text-slate-900 font-['Outfit'] flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <span>Immutable Governance Audit Trail</span>
          </h2>
          <p className="text-xs text-slate-500">
            Append-only historical ledger capturing every AI generation, human approval, rejection, and state mutation.
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2 text-xs">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-1.5 focus:outline-none focus:border-blue-500 font-medium"
          >
            <option value="">All Governance Actions</option>
            <option value="APPROVE">APPROVE</option>
            <option value="EDIT_APPROVE">EDIT & APPROVE</option>
            <option value="REJECT">REJECT</option>
            <option value="MATCH_GENERATED">MATCH_GENERATED</option>
            <option value="IMPORT">IMPORT</option>
          </select>

          <button
            onClick={fetchLogs}
            className="p-2 rounded-xl bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-slate-200 transition-colors shadow-xs"
            title="Refresh Audit Trail"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold text-[11px]">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-3">Action</th>
                <th className="py-3 px-3">Entity Type</th>
                <th className="py-3 px-3">Entity ID</th>
                <th className="py-3 px-4">Authorized Actor</th>
                <th className="py-3 px-4 text-right">State Diff</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
                    <span>Loading Audit Ledger...</span>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-400">
                    No audit records found matching current filter.
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isExpanded = expandedId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr
                        onClick={() => toggleExpand(log.id)}
                        className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : 'Just now'}
                        </td>
                        <td className="py-3 px-3">{getActionBadge(log.action)}</td>
                        <td className="py-3 px-3 font-semibold text-slate-800">{log.entity_type}</td>
                        <td className="py-3 px-3 font-mono text-blue-700 font-bold">#{log.entity_id || '—'}</td>
                        <td className="py-3 px-4 text-slate-700 flex items-center space-x-1.5 font-medium">
                          <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                          <span>{log.actor}</span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button className="text-[11px] text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center space-x-1">
                            <span>{isExpanded ? 'Hide Diff' : 'View Diff'}</span>
                            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-slate-50/70 border-b border-slate-200">
                          <td colSpan="6" className="p-4 space-y-3">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                              {/* Before State */}
                              <div className="p-3 bg-white rounded-xl border border-rose-200 shadow-xs">
                                <span className="font-bold block mb-1.5 font-sans uppercase text-[10px] tracking-wider text-rose-700">
                                  State Before Mutation
                                </span>
                                <pre className="text-slate-800 text-[11px] overflow-x-auto whitespace-pre-wrap">
                                  {log.before_state ? JSON.stringify(log.before_state, null, 2) : 'null (Initial Creation)'}
                                </pre>
                              </div>

                              {/* After State */}
                              <div className="p-3 bg-white rounded-xl border border-emerald-200 shadow-xs">
                                <span className="font-bold block mb-1.5 font-sans uppercase text-[10px] tracking-wider text-emerald-700">
                                  State After Mutation
                                </span>
                                <pre className="text-slate-800 text-[11px] overflow-x-auto whitespace-pre-wrap">
                                  {log.after_state ? JSON.stringify(log.after_state, null, 2) : 'null'}
                                </pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
