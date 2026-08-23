import React, { useState } from 'react';
import { X, Copy, Check, Download, Scale, ShieldAlert } from 'lucide-react';

export default function RegulatoryReportModal({ siteData, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!siteData || !siteData.site) return null;
  const { site, findings } = siteData;

  const generateReportText = () => {
    let report = `# FORMAL REGULATORY ENFORCEMENT DOSSIER
**SUBMITTED TO:** Federal Trade Commission (FTC) & EU Commission DSA Enforcement Directorate
**INVESTIGATION TARGET:** ${site.name} (${site.domain})
**DATE OF AUDIT:** ${new Date().toISOString().split('T')[0]}
**MANIPULATION INDEX SCORE:** ${site.manipulation_index} / 100 [GRADE: ${site.grade}]
**REGULATORY RISK CLASSIFICATION:** ${site.ftc_risk_level}

---

## 1. EXECUTIVE SUMMARY OF DECEPTIVE PRACTICES
Algorithmic audit of **${site.domain}** uncovered **${findings.length} actionable violations** of federal and international consumer protection standards. The investigated user flow systematically deployed manipulative interface design ("dark patterns") designed to subvert consumer autonomy, conceal mandatory transaction fees, and impose asymmetrical friction on contract cancellation.

---

## 2. STATUTORY VIOLATIONS CHARGE SHEET
`;

    findings.forEach((f, idx) => {
      report += `
### COUNT ${idx + 1}: ${f.pattern_name.toUpperCase()} [SEVERITY: ${f.severity.toUpperCase()}]
- **Category:** ${f.category}
- **Applicable Statutes:** ${f.regulatory_statute || "FTC Act Section 5(a)"} (${f.regulatory_citation || "15 U.S.C. § 45"})
- **Forensic Plain Proof:** ${f.plain_explanation}
- **DOM Selector Proof:** \`${f.dom_selector || "N/A"}\`
- **DOM Snippet:** \`${f.dom_snippet || "N/A"}\`
- **Psychological Coercion Mechanism:** ${f.psychological_mechanism || "Cognitive Bias Exploitation"}
- **Mandated Remediation Action:** ${f.remedy_recommendation || "Remove deceptive element immediately"}

`;
    });

    report += `
---

## 3. APPLICABLE LEGAL PRECEDENTS & RULES
1. **FTC Act Section 5 (15 U.S.C. § 45)**: Prohibition against unfair or deceptive acts or practices affecting commerce.
2. **FTC Click-to-Cancel Rule (16 CFR Part 425)**: Mandating that cancellation mechanisms must be as simple and direct as enrollment mechanisms.
3. **EU Digital Services Act (Regulation EU 2022/2065 Article 25)**: Strict ban on deceptive choice architecture and misleading interface framing.
4. **California Honest Pricing Law (SB 478 / Civ. Code § 1770)**: Prohibition against unadvertised drip fees and hidden handling charges.

**CERTIFIED BY HOUDINI AUTONOMOUS PROSECUTION ENGINE**
`;
    return report;
  };

  const reportText = generateReportText();

  const handleCopy = () => {
    navigator.clipboard.writeText(reportText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([reportText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `FTC_Dossier_${site.domain.replace('.', '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-3 sm:p-6 backdrop-blur-md">
      <div className="bg-[#121215] border border-white/10 w-full max-w-4xl max-h-[90vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-[#18181b]/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Scale className="w-4 h-4 text-blue-400" />
            <span className="font-semibold text-sm text-white">
              Official Regulatory Enforcement Dossier
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="bg-white/5 hover:bg-white/10 text-white px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 border border-white/10 cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .MD</span>
            </button>
            <button onClick={onClose} className="w-8 h-8 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center cursor-pointer ml-2">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Markdown Content Viewer */}
        <div className="p-6 overflow-y-auto bg-[#09090b] text-zinc-300 font-mono text-xs leading-relaxed space-y-4">
          <pre className="whitespace-pre-wrap font-mono text-xs text-zinc-300 select-all">
            {reportText}
          </pre>
        </div>

      </div>
    </div>
  );
}
