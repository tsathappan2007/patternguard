import React, { useState } from 'react';
import { X, FileText, Code, Scale, CheckCircle, Eye } from 'lucide-react';
import { apiUrl } from '../lib/api';

export default function EvidenceModal({ scanData, onClose, onOpenRegulatoryDossier }) {
  const [selectedFindingIndex, setSelectedFindingIndex] = useState(0);

  if (!scanData) return null;

  const siteName = scanData.site_name || scanData.domain || 'Audited Target';
  const domain = scanData.domain || '';
  const manipulationIndex = scanData.score_summary?.manipulation_index ?? 0;
  const grade = scanData.score_summary?.grade || 'N/A';
  const findings = scanData.findings || [];
  const currentFinding = findings.length > 0 ? findings[selectedFindingIndex] : null;

  const getSeverityBadge = (severity) => {
    if (severity === 'Critical') return 'bg-[#ff6b6b]/10 border-[#ff6b6b]/30 text-[#ff6b6b]';
    if (severity === 'High') return 'bg-[#ffa94d]/10 border-[#ffa94d]/30 text-[#ffa94d]';
    return 'bg-[#6798ff]/10 border-[#6798ff]/30 text-[#6798ff]';
  };

  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-3 sm:p-6 backdrop-blur-md overflow-y-auto font-sans">
      <div className="bg-[#141414] border border-[#1e1e1e] w-full max-w-5xl max-h-[92vh] rounded-[8px] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Top Header */}
        <div className="p-4 sm:p-5 bg-[#141414] border-b border-[#1e1e1e] flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-[6px] bg-[#1e1e1e] border border-[#313131] flex items-center justify-center font-mono font-bold text-[14px] text-[#6798ff]">
              {grade}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-[16px] font-medium text-white">{siteName}</h3>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-[4px] bg-[#0a0a0a] border border-[#1e1e1e] text-[#7c7c7c]">
                  {domain}
                </span>
              </div>
              <div className="text-[12px] font-mono text-[#a7a7a7] mt-0.5">
                MANIPULATION INDEX: <span className="text-white font-bold">{manipulationIndex.toFixed(1)}/100</span> · {findings.length} VIOLATIONS RECORDED
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onOpenRegulatoryDossier(scanData)}
              className="bg-[#1e1e1e] hover:bg-[#282828] text-white px-3 py-1.5 rounded-[6px] text-[12px] font-mono flex items-center gap-1.5 border border-[#313131] transition-colors cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5 text-[#6798ff]" />
              <span>Export Regulatory Dossier</span>
            </button>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-[4px] hover:bg-white/10 text-[#a7a7a7] hover:text-white transition-colors flex items-center justify-center cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 bg-[#0f0f0f]">
          
          {/* Left Column: Proofs Selector & Viewport Screenshot */}
          <div className="lg:col-span-7 flex flex-col space-y-4">
            
            {/* Finding Tabs */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-[#1e1e1e]">
              <span className="text-[10px] font-mono text-[#7c7c7c] uppercase tracking-wider mr-1">
                EVIDENCE TABS:
              </span>
              {findings.map((f, idx) => (
                <button
                  key={f.id || idx}
                  onClick={() => setSelectedFindingIndex(idx)}
                  className={`px-2.5 py-1 rounded-[4px] text-[11px] font-mono border whitespace-nowrap transition-all cursor-pointer ${
                    selectedFindingIndex === idx
                      ? 'bg-white text-black font-semibold border-white shadow-sm'
                      : 'bg-[#141414] text-[#a7a7a7] border-[#1e1e1e] hover:text-white'
                  }`}
                >
                  #{idx + 1} {f.pattern_name ? f.pattern_name.slice(0, 18) : 'Violation'}...
                </button>
              ))}
            </div>

            {/* Visual Screenshot Display */}
            <div className="border border-[#1e1e1e] rounded-[6px] bg-[#0a0a0a] p-2 flex flex-col items-center justify-center min-h-[320px] overflow-hidden">
              {currentFinding && (currentFinding.annotated_path || currentFinding.screenshot_path) ? (
                <div className="relative w-full h-full flex flex-col items-center">
                  <div className="w-full bg-[#141414] text-[#7c7c7c] text-[10px] font-mono py-1 px-2.5 rounded-t-[4px] mb-2 flex justify-between border-b border-[#1e1e1e]">
                    <span>DOM VIEWPORT CAPTURE</span>
                    <span className="text-[#6798ff]">● VERIFIED ELEMENT</span>
                  </div>
                  <img
                    src={apiUrl(currentFinding.annotated_path || currentFinding.screenshot_path)}
                    alt="Annotated Proof"
                    className="w-full h-auto max-h-[380px] object-contain rounded-[4px] border border-[#1e1e1e] bg-white"
                  />
                </div>
              ) : (
                <div className="text-[12px] text-[#555] font-mono text-center p-8">
                  [Visual viewport snapshot rendered in full-flow analysis]
                </div>
              )}
            </div>

            {/* DOM Selector Box */}
            {currentFinding && currentFinding.dom_selector && (
              <div className="border border-[#1e1e1e] rounded-[6px] bg-[#141414] p-3 text-[12px] space-y-1">
                <div className="font-mono text-[10px] text-[#7c7c7c] uppercase tracking-wider flex items-center gap-1.5">
                  <Code className="w-3 h-3 text-[#6798ff]" />
                  <span>Target DOM Selector Path</span>
                </div>
                <code className="font-mono text-[11px] text-[#ffd43b] break-all bg-[#0a0a0a] px-2.5 py-1 rounded-[4px] border border-[#1e1e1e] block">
                  {currentFinding.dom_selector}
                </code>
              </div>
            )}
          </div>

          {/* Right Column: Violation Details */}
          <div className="lg:col-span-5 flex flex-col space-y-3">
            {currentFinding ? (
              <div className="border border-[#1e1e1e] rounded-[6px] bg-[#141414] p-5 flex flex-col justify-between h-full space-y-4">
                <div className="space-y-3.5">
                  
                  {/* Category & Severity */}
                  <div className="flex items-center justify-between pb-3 border-b border-[#1e1e1e]">
                    <span className="font-mono text-[11px] text-[#7c7c7c] uppercase">
                      Category: <strong className="text-white">{currentFinding.category}</strong>
                    </span>
                    <span className={`px-2 py-0.5 rounded-[4px] text-[10px] font-mono border uppercase ${getSeverityBadge(currentFinding.severity)}`}>
                      {currentFinding.severity} (+{currentFinding.score_impact} pts)
                    </span>
                  </div>

                  {/* Pattern Name */}
                  <h4 className="text-[15px] font-medium text-white">
                    {currentFinding.pattern_name}
                  </h4>

                  {/* Forensic Proof */}
                  <div className="text-[12px] text-[#a7a7a7] leading-[1.5]">
                    <span className="text-[10px] font-mono text-[#7c7c7c] uppercase block mb-1">Forensic Analysis:</span>
                    <p className="bg-[#0a0a0a] p-3 rounded-[6px] border border-[#1e1e1e] text-[#ccc]">
                      {currentFinding.plain_explanation}
                    </p>
                  </div>

                  {/* Psychological Mechanism */}
                  {currentFinding.psychological_mechanism && (
                    <div className="text-[12px] leading-[1.5]">
                      <span className="text-[10px] font-mono text-[#ffa94d] uppercase block mb-1">Cognitive Mechanism:</span>
                      <p className="text-[#ffa94d]/90 bg-[#ffa94d]/10 p-2.5 rounded-[6px] border border-[#ffa94d]/20 text-[11px]">
                        {currentFinding.psychological_mechanism}
                      </p>
                    </div>
                  )}

                  {/* Statutory Law */}
                  <div className="border-t border-[#1e1e1e] pt-3 text-[12px]">
                    <span className="text-[10px] font-mono text-[#ff6b6b] uppercase flex items-center gap-1 mb-1">
                      <Scale className="w-3.5 h-3.5" />
                      <span>Applicable Consumer Statute:</span>
                    </span>
                    <div className="font-mono text-[11px] text-[#ff6b6b]/90 bg-[#ff6b6b]/10 p-2.5 rounded-[6px] border border-[#ff6b6b]/20">
                      <div>{currentFinding.regulatory_statute || "FTC Act Section 5"}</div>
                      <div className="text-[10px] text-[#aaa] mt-0.5">{currentFinding.regulatory_citation}</div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#1e1e1e] flex items-center justify-between text-[10px] font-mono text-[#7c7c7c]">
                  <span>RECORD ID: {currentFinding.id || 'N/A'}</span>
                  <span className="text-[#a7a7a7]">HEURISTIC RESULT · REVIEW RECOMMENDED</span>
                </div>
              </div>
            ) : (
              <div className="border border-[#1e1e1e] rounded-[6px] p-8 text-center text-[12px] text-[#555]">
                Select an evidence tab to inspect details.
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
