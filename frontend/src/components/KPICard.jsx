import React from 'react';

export default function KPICard({ title, value, subtitle, icon: Icon, badge, color = 'blue' }) {
  const colorMap = {
    blue: {
      border: 'border-slate-200 hover:border-blue-300',
      iconBg: 'bg-blue-50 text-blue-600',
      badge: 'bg-blue-50 text-blue-700 border-blue-200'
    },
    emerald: {
      border: 'border-slate-200 hover:border-emerald-300',
      iconBg: 'bg-emerald-50 text-emerald-600',
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200'
    },
    amber: {
      border: 'border-slate-200 hover:border-amber-300',
      iconBg: 'bg-amber-50 text-amber-600',
      badge: 'bg-amber-50 text-amber-700 border-amber-200'
    },
    purple: {
      border: 'border-slate-200 hover:border-purple-300',
      iconBg: 'bg-purple-50 text-purple-600',
      badge: 'bg-purple-50 text-purple-700 border-purple-200'
    }
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className={`glass-panel glass-panel-hover rounded-2xl p-5 border ${scheme.border} bg-white relative overflow-hidden group shadow-xs`}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">{title}</span>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight font-['Outfit']">{value}</div>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${scheme.iconBg} group-hover:scale-105 transition-transform duration-300`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between pt-2.5 border-t border-slate-100">
        <span className="text-xs text-slate-500 font-medium">{subtitle}</span>
        {badge && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${scheme.badge}`}>
            {badge}
          </span>
        )}
      </div>
    </div>
  );
}
