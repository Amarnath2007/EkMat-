import React from 'react';

export default function KPICard({ title, value, subtitle, icon: Icon, badge, color = 'blue' }) {
  const colorMap = {
    blue: {
      bg: 'from-blue-600/20 to-blue-800/10',
      border: 'border-blue-500/30',
      iconBg: 'bg-blue-500/20 text-blue-400',
      badge: 'bg-blue-900/60 text-blue-300 border-blue-500/30'
    },
    emerald: {
      bg: 'from-emerald-600/20 to-emerald-800/10',
      border: 'border-emerald-500/30',
      iconBg: 'bg-emerald-500/20 text-emerald-400',
      badge: 'bg-emerald-900/60 text-emerald-300 border-emerald-500/30'
    },
    amber: {
      bg: 'from-amber-600/20 to-amber-800/10',
      border: 'border-amber-500/30',
      iconBg: 'bg-amber-500/20 text-amber-400',
      badge: 'bg-amber-900/60 text-amber-300 border-amber-500/30'
    },
    purple: {
      bg: 'from-purple-600/20 to-purple-800/10',
      border: 'border-purple-500/30',
      iconBg: 'bg-purple-500/20 text-purple-400',
      badge: 'bg-purple-900/60 text-purple-300 border-purple-500/30'
    }
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className={`glass-panel glass-panel-hover rounded-2xl p-5 border ${scheme.border} bg-gradient-to-br ${scheme.bg} relative overflow-hidden group`}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block mb-1">{title}</span>
          <div className="text-3xl font-extrabold text-white tracking-tight">{value}</div>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${scheme.iconBg} group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-800/60">
        <span className="text-xs text-slate-400">{subtitle}</span>
        {badge && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${scheme.badge}`}>
            {badge}
          </span>
        )}
      </div>
    </div>
  );
}
