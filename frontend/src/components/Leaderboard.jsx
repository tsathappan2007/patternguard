import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, ChevronRight, Scale, Search, Eye, Filter, ArrowUpRight } from 'lucide-react';

export default function Leaderboard({ sites, onSelectSite, onOpenScanner }) {
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredSites = (sites || []).filter(site => {
    const matchesSearch = site.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          site.domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          site.primary_pattern.toLowerCase().includes(searchQuery.toLowerCase());
    if (filterCategory === 'ALL') return matchesSearch;
    if (filterCategory === 'Clean') return matchesSearch && site.manipulation_index <= 20;
    return matchesSearch && (site.category.includes(filterCategory.split(' ')[0]) || site.category === filterCategory);
  });

  const getScoreBadge = (score) => {
    if (score >= 70) return 'text-red-400 bg-red-500/10 border-red-500/20';
    if (score >= 45) return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
    if (score >= 20) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
  };

  const getBarColor = (score) => {
    if (score >= 70) return 'bg-red-500 shadow-sm shadow-red-500/50';
    if (score >= 45) return 'bg-orange-500 shadow-sm shadow-orange-500/50';
    if (score >= 20) return 'bg-amber-500 shadow-sm shadow-amber-500/50';
    return 'bg-emerald-500 shadow-sm shadow-emerald-500/50';
  };

  return (
    <section id="leaderboard" className="w-full py-16 px-6 bg-[#09090b]">
      <div className="max-w-[1280px] mx-auto space-y-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400 uppercase tracking-wider mb-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
              <span>Registry of Audited Sites</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-semibold text-white tracking-tight">
              Hall of Shame: Manipulation Index
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1">
              Live websites ranked by deceptive UX score and regulatory liability (0–100).
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search domain, brand, or pattern..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-[#121215] border border-white/10 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-blue-500 w-full sm:w-64 transition-all"
            />
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          {[
            { id: 'ALL', label: 'All Sites' },
            { id: 'E-Commerce / Consumer Goods', label: 'E-Commerce' },
            { id: 'SaaS / Subscription Services', label: 'SaaS & Subscriptions' },
            { id: 'Travel & Hospitality', label: 'Travel & Airlines' },
            { id: 'Clean', label: 'Ethical (Grade A)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterCategory(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
                filterCategory === tab.id
                  ? 'bg-white text-black font-semibold'
                  : 'bg-[#141417] text-zinc-400 hover:text-white hover:bg-[#1e1e24] border border-white/5'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Table Container */}
        <div className="rounded-2xl border border-white/10 bg-[#121215]/80 backdrop-blur-xl overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/10 bg-[#18181b]/50 text-zinc-400 font-mono text-[11px] uppercase tracking-wider">
                  <th className="py-4 px-5 font-medium w-12 text-center">#</th>
                  <th className="py-4 px-5 font-medium">Domain & Target</th>
                  <th className="py-4 px-5 font-medium">Category</th>
                  <th className="py-4 px-5 font-medium">Primary Violation</th>
                  <th className="py-4 px-5 font-medium w-52">Manipulation Index</th>
                  <th className="py-4 px-5 font-medium">Risk Status</th>
                  <th className="py-4 px-5 font-medium text-right">Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredSites.map((site, index) => {
                  const score = site.manipulation_index;
                  return (
                    <tr
                      key={site.id}
                      onClick={() => onSelectSite(site.id)}
                      className="hover:bg-white/[0.03] transition-colors group cursor-pointer"
                    >
                      {/* Rank */}
                      <td className="py-4 px-5 text-center font-mono text-zinc-500 font-semibold">
                        {index + 1}
                      </td>

                      {/* Domain & Target */}
                      <td className="py-4 px-5">
                        <div className="font-medium text-white text-sm group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                          <span>{site.name}</span>
                        </div>
                        <div className="font-mono text-[11px] text-zinc-500">{site.domain}</div>
                      </td>

                      {/* Category */}
                      <td className="py-4 px-5 text-zinc-400">
                        <span className="inline-block px-2.5 py-1 rounded-md bg-white/5 border border-white/5 text-[11px]">
                          {site.category.split('/')[0]}
                        </span>
                      </td>

                      {/* Primary Violation */}
                      <td className="py-4 px-5">
                        <div className="font-medium text-zinc-200">{site.top_violation || site.primary_pattern}</div>
                        <div className="text-[10px] text-zinc-500 font-mono mt-0.5">
                          Class: {site.primary_pattern}
                        </div>
                      </td>

                      {/* Score Bar */}
                      <td className="py-4 px-5">
                        <div className="flex items-center justify-between font-mono mb-1.5">
                          <span className="font-bold text-sm text-white">{score.toFixed(1)}</span>
                          <span className="text-[10px] text-zinc-500 font-mono">/ 100 [GRADE {site.grade}]</span>
                        </div>
                        <div className="w-full bg-zinc-800/80 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${getBarColor(score)} transition-all duration-500`}
                            style={{ width: `${Math.min(100, Math.max(4, score))}%` }}
                          ></div>
                        </div>
                      </td>

                      {/* Risk Badge */}
                      <td className="py-4 px-5">
                        <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-mono border ${getScoreBadge(score)}`}>
                          {site.ftc_risk_level}
                        </span>
                      </td>

                      {/* Action Button */}
                      <td className="py-4 px-5 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectSite(site.id);
                          }}
                          className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-medium cursor-pointer"
                        >
                          <span>Inspect Proof</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {filteredSites.length === 0 && (
              <div className="py-16 text-center text-zinc-500 text-xs">
                No matching entries found. Enter a URL above to audit live.
              </div>
            )}
          </div>
        </div>

      </div>
    </section>
  );
}
