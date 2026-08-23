import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Scale, Search, Eye, ArrowUpRight, Trash2, Globe, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function InspectionLedger({ scanHistory, onSelectScan, onClearHistory, onOpenScanner }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const filteredScans = (scanHistory || []).filter(item => {
    const nameMatch = (item.site_name || item.domain || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                      (item.primary_pattern || '').toLowerCase().includes(searchQuery.toLowerCase());
    if (!nameMatch) return false;
    if (filterSeverity === 'ALL') return true;
    if (filterSeverity === 'CRITICAL') return item.score_summary?.manipulation_index >= 60;
    if (filterSeverity === 'MODERATE') return item.score_summary?.manipulation_index >= 25 && item.score_summary?.manipulation_index < 60;
    if (filterSeverity === 'CLEAN') return item.score_summary?.manipulation_index < 25;
    return true;
  });

  const getScoreColor = (score) => {
    if (score >= 60) return 'text-[#ff6b6b] bg-[#ff6b6b]/10 border-[#ff6b6b]/30';
    if (score >= 25) return 'text-[#ffa94d] bg-[#ffa94d]/10 border-[#ffa94d]/30';
    return 'text-[#51cf66] bg-[#51cf66]/10 border-[#51cf66]/30';
  };

  const getBarColor = (score) => {
    if (score >= 60) return 'bg-[#ff6b6b]';
    if (score >= 25) return 'bg-[#ffa94d]';
    return 'bg-[#51cf66]';
  };

  return (
    <div className="w-full min-h-[calc(100vh-56px)] bg-[#0a0a0a] text-white py-12 px-6 font-sans">
      <div className="max-w-[1200px] mx-auto space-y-8">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-[#1e1e1e]">
          <div>
            <div className="flex items-center gap-2 text-[12px] font-mono text-[#a7a7a7] uppercase tracking-[0.85px] mb-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#6798ff]"></span>
              <span>Local Forensic Registry</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-medium tracking-tight text-white">
              Compliance Observatory & Audit Ledger
            </h1>
            <p className="text-[14px] text-[#a7a7a7] mt-1">
              Locally stored audit trail of analyzed funnels, deception scores, and statutory evidence.
            </p>
          </div>

          {/* Search & Actions */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#7c7c7c] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search audited domains..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#141414] border border-[#1e1e1e] rounded-[6px] pl-9 pr-3 py-1.5 text-[13px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] w-full sm:w-64 font-mono"
              />
            </div>

            {scanHistory && scanHistory.length > 0 && (
              <button
                onClick={onClearHistory}
                className="p-2 rounded-[6px] bg-[#141414] hover:bg-[#1e1e1e] border border-[#1e1e1e] text-[#7c7c7c] hover:text-[#ff6b6b] transition-colors cursor-pointer"
                title="Clear local audit history"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center justify-between gap-4 text-[12px] font-mono">
          <div className="flex items-center gap-2">
            {[
              { id: 'ALL', label: 'All Audited' },
              { id: 'CRITICAL', label: 'High Liability (60+)' },
              { id: 'MODERATE', label: 'Moderate (25-59)' },
              { id: 'CLEAN', label: 'Compliant (<25)' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilterSeverity(tab.id)}
                className={`px-3 py-1.5 rounded-[6px] transition-all cursor-pointer ${
                  filterSeverity === tab.id
                    ? 'bg-white text-black font-semibold'
                    : 'bg-[#141414] text-[#a7a7a7] hover:text-white border border-[#1e1e1e]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <span className="text-[#7c7c7c]">
            {filteredScans.length} {filteredScans.length === 1 ? 'RECORD' : 'RECORDS'} SAVED LOCALLY
          </span>
        </div>

        {/* Audit Registry Table */}
        <div className="rounded-[8px] border border-[#1e1e1e] bg-[#141414] overflow-hidden shadow-2xl">
          {filteredScans.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[13px] border-collapse">
                <thead>
                  <tr className="border-b border-[#1e1e1e] bg-[#111111] text-[#a7a7a7] font-mono text-[11px] uppercase tracking-wider">
                    <th className="py-3.5 px-5 font-medium w-12 text-center">#</th>
                    <th className="py-3.5 px-5 font-medium">Domain & Target</th>
                    <th className="py-3.5 px-5 font-medium">Flow Type</th>
                    <th className="py-3.5 px-5 font-medium">Findings</th>
                    <th className="py-3.5 px-5 font-medium w-52">Manipulation Index</th>
                    <th className="py-3.5 px-5 font-medium">Status</th>
                    <th className="py-3.5 px-5 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e1e1e]">
                  {filteredScans.map((item, index) => {
                    const score = item.score_summary?.manipulation_index || 0;
                    const grade = item.score_summary?.grade || 'N/A';
                    return (
                      <tr
                        key={item.scan_id || index}
                        onClick={() => onSelectScan(item)}
                        className="hover:bg-white/[0.02] transition-colors cursor-pointer group"
                      >
                        <td className="py-4 px-5 text-center font-mono text-[#555]">
                          {index + 1}
                        </td>

                        <td className="py-4 px-5">
                          <div className="font-medium text-white group-hover:text-[#6798ff] transition-colors">
                            {item.site_name || item.domain}
                          </div>
                          <div className="font-mono text-[11px] text-[#7c7c7c] mt-0.5">
                            {item.domain}
                          </div>
                        </td>

                        <td className="py-4 px-5 text-[#a7a7a7] font-mono text-[12px] uppercase">
                          <span className="px-2 py-0.5 rounded-[4px] bg-[#0a0a0a] border border-[#1e1e1e]">
                            {item.flow_type || 'checkout'}
                          </span>
                        </td>

                        <td className="py-4 px-5">
                          <span className="font-mono text-white font-medium">
                            {item.findings?.length || 0}
                          </span>
                          <span className="text-[#7c7c7c] text-[11px] ml-1">violations</span>
                        </td>

                        <td className="py-4 px-5">
                          <div className="flex items-center justify-between font-mono mb-1 text-[12px]">
                            <span className="font-bold text-white">{score.toFixed(1)}</span>
                            <span className="text-[#7c7c7c] text-[10px]">/ 100 [GRADE {grade}]</span>
                          </div>
                          <div className="w-full bg-[#0a0a0a] rounded-full h-1.5 overflow-hidden border border-[#313131]">
                            <div
                              className={`h-full ${getBarColor(score)} transition-all duration-300`}
                              style={{ width: `${Math.min(100, Math.max(4, score))}%` }}
                            ></div>
                          </div>
                        </td>

                        <td className="py-4 px-5">
                          <span className={`inline-block px-2.5 py-0.5 rounded-[4px] text-[11px] font-mono border ${getScoreColor(score)}`}>
                            {item.score_summary?.ftc_risk_level || (score >= 60 ? 'Critical Liability' : score >= 25 ? 'Moderate Risk' : 'Compliant')}
                          </span>
                        </td>

                        <td className="py-4 px-5 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectScan(item);
                            }}
                            className="text-[13px] text-[#6798ff] hover:underline font-medium cursor-pointer inline-flex items-center gap-1"
                          >
                            <span>Inspect Evidence</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-20 px-6 text-center space-y-4">
              <div className="w-12 h-12 rounded-[8px] bg-[#1e1e1e] border border-[#313131] flex items-center justify-center text-[#6798ff] mx-auto">
                <Globe className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-[16px] font-medium text-white">No Audited Funnels in Local Registry</h3>
                <p className="text-[13px] text-[#a7a7a7] max-w-sm mx-auto">
                  Run a live audit on any website to automatically record its DOM proofs and manipulation score in your browser.
                </p>
              </div>
              <div className="pt-2">
                <button
                  onClick={onOpenScanner}
                  className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-4 py-2 rounded-[6px] text-[13px] font-medium transition-all inline-flex items-center gap-1.5 cursor-pointer shadow-sm"
                >
                  <span>Launch First Audit →</span>
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

