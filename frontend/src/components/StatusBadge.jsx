import React from 'react';

export default function StatusBadge({ status, type = 'status' }) {
  const s = (status || '').toUpperCase();

  if (type === 'confidence') {
    if (s === 'HIGH') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-900/60 text-emerald-300 border border-emerald-500/40 glow-emerald">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
          HIGH CONFIDENCE
        </span>
      );
    }
    if (s === 'MEDIUM') {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-900/50 text-amber-300 border border-amber-500/40 glow-amber">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mr-1.5"></span>
          MEDIUM REVIEW
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
        LOW (DISTINCT)
      </span>
    );
  }

  // General Status (PENDING, APPROVED, REJECTED, EDITED_APPROVED)
  if (s === 'APPROVED' || s === 'EDITED_APPROVED') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-600/50">
        <svg className="w-3.5 h-3.5 mr-1 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
        </svg>
        {s === 'EDITED_APPROVED' ? 'EDITED & APPROVED' : 'APPROVED'}
      </span>
    );
  }

  if (s === 'REJECTED') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-300 border border-rose-600/40">
        <svg className="w-3.5 h-3.5 mr-1 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        REJECTED
      </span>
    );
  }

  // PENDING (Default)
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-300 border border-blue-600/40">
      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mr-1.5"></span>
      PENDING REVIEW
    </span>
  );
}
