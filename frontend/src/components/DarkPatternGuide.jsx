import React from 'react';
import { X, BookOpen, ShieldCheck, Scale, CheckCircle, Zap } from 'lucide-react';

export default function DarkPatternGuide({ onClose }) {
  const rubrics = [
    {
      category: "Sneaking / Pre-selected Add-ons",
      trigger: "Pre-checked checkboxes (`checked=true`), auto-injected cart line items (warranties, expedited handling, carbon offsets, recurring memberships).",
      severity: "Critical (+25 to +30 pts)",
      statute: "FTC Act § 5 (Unfair/Deceptive Practices); EU DSA Art. 25; Cal. AB 390",
      mechanism: "Default Effect / Inertia Bias"
    },
    {
      category: "Hidden Costs / Drip Pricing",
      trigger: "Mandatory fees (convenience fee, platform service fee, mandatory handling) revealed late in checkout steps that were absent from headline prices.",
      severity: "Critical (+22 to +28 pts)",
      statute: "FTC 16 CFR Part 464 (Deceptive Fees Rule); Cal. SB 478 (Honest Pricing Law)",
      mechanism: "Sunk Cost Fallacy & Bait-and-Switch"
    },
    {
      category: "Confirmshaming / Coercive Opt-Out",
      trigger: "Decline/skip buttons framed in identity-derogating or guilt-tripping language (e.g., 'No thanks, I hate saving money', 'I don't care about my security').",
      severity: "High (+24 pts)",
      statute: "FTC Policy Statement on Dark Patterns; EU DSA Art. 25(1)",
      mechanism: "Emotional Manipulation & Guilt Induction"
    },
    {
      category: "Fake Urgency / Resetting Timers",
      trigger: "Countdown clocks that reset to initial state upon page reload; synthetic scarcity warnings ('Only 1 left!') with no backend inventory depletion.",
      severity: "Critical (+28 pts)",
      statute: "FTC Urgency Enforcement Guidance; EU UCPD Annex I Item 7",
      mechanism: "Artificial Scarcity & Panic FOMO"
    },
    {
      category: "Obstruction / Roach Motel",
      trigger: "1-click instant enrollment vs multi-step cancellation labyrinth (>= 3 screens, exit interviews, guilt screens) or mandatory phone-call walls.",
      severity: "Critical (+30 to +35 pts)",
      statute: "FTC Click-to-Cancel Mandate (16 CFR § 425.6); Cal. SB 313",
      mechanism: "Sludge & Cognitive Friction"
    },
    {
      category: "Visual Deception / Low-Contrast Disclosures",
      trigger: "Auto-renewal terms and opt-out text rendered with < 3.0:1 contrast ratio against background, or micro-font sizes < 11px.",
      severity: "High (+18 to +26 pts)",
      statute: "FTC Conspicuousness Standards (16 CFR § 425.4); WCAG 2.1 Level AA",
      mechanism: "Visual Suppression & Concealment"
    }
  ];

  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-3 sm:p-6 backdrop-blur-md">
      <div className="bg-[#121215] border border-white/10 w-full max-w-5xl max-h-[90vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-[#18181b]/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <h3 className="text-base font-semibold text-white">Detection Rubric & Statutory Grounding</h3>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Table */}
        <div className="p-6 overflow-y-auto space-y-5">
          <div className="border border-white/10 rounded-xl overflow-hidden bg-[#18181b]/40">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-white/10 bg-[#18181b]/80 font-mono text-zinc-400 text-[11px] uppercase tracking-wider">
                  <th className="p-4 font-medium">Category</th>
                  <th className="p-4 font-medium">Algorithmic Trigger</th>
                  <th className="p-4 font-medium">Score Weight</th>
                  <th className="p-4 font-medium">Legal Grounding</th>
                  <th className="p-4 font-medium">Cognitive Bias</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {rubrics.map((r, i) => (
                  <tr key={i} className="hover:bg-white/[0.02]">
                    <td className="p-4 font-medium text-white">{r.category}</td>
                    <td className="p-4 text-zinc-300 leading-relaxed">{r.trigger}</td>
                    <td className="p-4 font-mono font-semibold text-red-400">{r.severity}</td>
                    <td className="p-4 font-mono text-[11px] text-zinc-400">{r.statute}</td>
                    <td className="p-4 text-zinc-400 italic text-[11px]">{r.mechanism}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
