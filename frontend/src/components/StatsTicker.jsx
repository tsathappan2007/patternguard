import React from 'react';
import { ShieldCheck, AlertTriangle, Scale, Activity } from 'lucide-react';

export default function StatsTicker({ stats }) {
  const defaultStats = {
    total_sites_audited: 5,
    total_patterns_prosecuted: 14,
    ftc_violations_flagged: 9,
    avg_manipulation_index: 63.8
  };

  const currentStats = stats || defaultStats;

  const cards = [
    {
      label: 'SITES AUDITED',
      value: currentStats.total_sites_audited,
      icon: Activity,
      color: 'text-blue-400',
      badge: 'Active Registry'
    },
    {
      label: 'PATTERNS PROSECUTED',
      value: currentStats.total_patterns_prosecuted,
      icon: AlertTriangle,
      color: 'text-red-400',
      badge: 'Forensic Proofs'
    },
    {
      label: 'REGULATORY VIOLATIONS',
      value: currentStats.ftc_violations_flagged,
      icon: Scale,
      color: 'text-orange-400',
      badge: 'FTC & EU DSA'
    },
    {
      label: 'AVG MANIPULATION INDEX',
      value: `${currentStats.avg_manipulation_index}/100`,
      icon: ShieldCheck,
      color: 'text-indigo-400',
      badge: 'Score Mean'
    },
  ];

  return (
    <section className="w-full bg-[#09090b] py-8 px-6 border-b border-white/5">
      <div className="max-w-[1280px] mx-auto grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c, i) => {
          const Icon = c.icon;
          return (
            <div
              key={i}
              className="p-4 rounded-xl bg-[#121215] border border-white/5 flex flex-col justify-between hover:border-white/10 transition-colors"
            >
              <div className="flex items-center justify-between text-zinc-500 mb-2">
                <span className="text-[10px] font-mono tracking-wider uppercase font-medium">{c.label}</span>
                <Icon className={`w-3.5 h-3.5 ${c.color}`} />
              </div>
              <div className="flex items-baseline justify-between">
                <span className="text-xl sm:text-2xl font-semibold text-white font-mono">{c.value}</span>
                <span className="text-[10px] text-zinc-500 font-mono">{c.badge}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
