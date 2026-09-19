import React from 'react';
import { Brain, AlignLeft, Cpu, ShieldCheck } from 'lucide-react';

export default function ScoreBreakdown({ semantic = 0, fuzzy = 0, attribute = 0, weighted = 0, band = 'MEDIUM' }) {
  const semPct = Math.round(semantic * 100);
  const fuzPct = Math.round(fuzzy * 100);
  const attrPct = Math.round(attribute * 100);
  const wtPct = Math.round(weighted * 100);

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-blue-600" />
          <span className="text-sm font-bold text-slate-800">Confidence Scoring Engine</span>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold tracking-tight text-slate-900">{wtPct}%</span>
          <span className="text-xs text-slate-500 block">Weighted Confidence</span>
        </div>
      </div>

      <div className="space-y-3 text-xs">
        {/* Signal 1: SBERT Semantic */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-700 font-medium">
              <Brain className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
              Semantic Embedding (SBERT all-MiniLM-L6-v2)
            </span>
            <span className="text-slate-600 font-semibold">{semPct}% <span className="text-[10px] text-slate-400 font-normal">(50% wt)</span></span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, semPct))}%` }}
            ></div>
          </div>
        </div>

        {/* Signal 2: RapidFuzz Lexical */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-700 font-medium">
              <AlignLeft className="w-3.5 h-3.5 mr-1.5 text-sky-600" />
              Lexical Similarity (RapidFuzz Token Sort/Set)
            </span>
            <span className="text-slate-600 font-semibold">{fuzPct}% <span className="text-[10px] text-slate-400 font-normal">(30% wt)</span></span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-sky-500 to-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, fuzPct))}%` }}
            ></div>
          </div>
        </div>

        {/* Signal 3: Technical Attributes */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="flex items-center text-slate-700 font-medium">
              <Cpu className="w-3.5 h-3.5 mr-1.5 text-emerald-600" />
              Technical Spec Compatibility (Type, Size, Class)
            </span>
            <span className="text-slate-600 font-semibold">{attrPct}% <span className="text-[10px] text-slate-400 font-normal">(20% wt)</span></span>
          </div>
          <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                attrPct === 0 ? 'bg-rose-500' : 'bg-gradient-to-r from-emerald-500 to-teal-600'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, attrPct))}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="bg-slate-50 rounded-lg p-2.5 border border-slate-200 text-[11px] text-slate-600">
        <span className="font-semibold text-slate-800">Routing Policy: </span>
        <code className="text-blue-800 bg-white px-1.5 py-0.5 rounded border border-slate-200 text-[10px] font-mono">
          Score = 0.50×Semantic + 0.30×Fuzzy + 0.20×Attributes
        </code>
        <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-500 font-medium">
          <span>HIGH: &gt;90% (Suggested Approval)</span>
          <span>MED: 60–90% (Human Review)</span>
          <span>LOW: &lt;60% (Distinct)</span>
        </div>
      </div>
    </div>
  );
}
