import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import HeroBand from './components/HeroBand';
import FlowStudio from './components/FlowStudio';
import InspectionLedger from './components/InspectionLedger';
import EvidenceModal from './components/EvidenceModal';
import SandboxSimulator from './components/SandboxSimulator';
import DarkPatternGuide from './components/DarkPatternGuide';
import RegulatoryReportModal from './components/RegulatoryReportModal';
import ApiKeyModal from './components/ApiKeyModal';

const STORAGE_KEY = 'pattern_guard_scan_history';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'studio' | 'registry'
  
  // Local cache, hydrated from the server's persisted scan registry when available.
  const [scanHistory, setScanHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [selectedScanData, setSelectedScanData] = useState(null);
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState(false);
  const [isSandboxOpen, setIsSandboxOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);
  const [dossierData, setDossierData] = useState(null);

  const [scannerParams, setScannerParams] = useState({
    url: 'http://127.0.0.1:8000/mock/shopsneak',
    name: 'ShopSneak Store',
    flow: 'checkout'
  });

  useEffect(() => {
    const controller = new AbortController();
    fetch('/api/scans?limit=50', { signal: controller.signal })
      .then(response => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then(data => {
        if (!Array.isArray(data.scans)) return;
        setScanHistory(previous => {
          const merged = [...data.scans, ...previous];
          return merged.filter((item, index) =>
            merged.findIndex(candidate => candidate.scan_id === item.scan_id) === index
          );
        });
      })
      .catch(error => {
        if (error.name !== 'AbortError') console.warn('Using local audit history:', error.message);
      });
    return () => controller.abort();
  }, []);

  // Cache completed scans locally so the registry remains useful while offline.
  const saveScanToLocalStorage = (newScanResult) => {
    setScanHistory(prev => {
      const filtered = prev.filter(item => item.scan_id !== newScanResult.scan_id);
      const updated = [newScanResult, ...filtered].slice(0, 50);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (err) {
        console.error('Failed to save to localStorage:', err);
      }
      return updated;
    });
  };

  const handleClearHistory = () => {
    localStorage.removeItem(STORAGE_KEY);
    setScanHistory([]);
  };

  const handleSelectScan = (scanItem) => {
    setSelectedScanData(scanItem);
    setIsEvidenceModalOpen(true);
  };

  const handleOpenStudioForScan = (scanItem) => {
    setSelectedScanData(scanItem);
    setActiveTab('studio');
  };

  const handleOpenDossier = (scanItem) => {
    setDossierData(scanItem);
    setIsDossierOpen(true);
  };

  const handleQuickScan = (url, name, flow) => {
    setScannerParams({ url, name, flow });
    setSelectedScanData(null);
    setActiveTab('studio');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#ededed] flex flex-col font-sans selection:bg-[#6798ff] selection:text-black">
      {/* Sleek Minimal Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        scanCount={scanHistory.length}
        onOpenScanner={() => setActiveTab('studio')}
        onOpenSandbox={() => setIsSandboxOpen(true)}
        onOpenGuide={() => setIsGuideOpen(true)}
        onOpenApiKeyModal={() => setIsApiKeyModalOpen(true)}
      />

      {/* Main View Area */}
      <main className="flex-1">
        {activeTab === 'home' && (
          <HeroBand
            onOpenScanner={() => setActiveTab('studio')}
            onOpenSandbox={() => setIsSandboxOpen(true)}
            onQuickScan={handleQuickScan}
          />
        )}

        {activeTab === 'studio' && (
          <FlowStudio
            initialScanData={selectedScanData}
            initialParams={scannerParams}
            onScanComplete={(result) => {
              saveScanToLocalStorage(result);
            }}
            onOpenApiKeyModal={() => setIsApiKeyModalOpen(true)}
            onOpenDossier={handleOpenDossier}
          />
        )}

        {activeTab === 'registry' && (
          <InspectionLedger
            scanHistory={scanHistory}
            onSelectScan={handleSelectScan}
            onClearHistory={handleClearHistory}
            onOpenScanner={() => setActiveTab('studio')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="w-full bg-[#0a0a0a] text-[#7c7c7c] border-t border-[#1e1e1e] py-10 px-6 font-sans">
        <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-6 text-[13px]">
          <div>
            <div className="font-medium text-white tracking-tight text-[14px]">
              Pattern Guard Autonomous Compliance Auditor
            </div>
            <div className="text-[#555] mt-0.5 max-w-md font-mono text-[11px]">
              Forensic deceptive UX detection & regulatory evidence generation. All records stored locally in browser.
            </div>
          </div>

          <div className="flex items-center gap-5 text-[12px] font-mono text-[#7c7c7c]">
            <button
              onClick={() => setActiveTab('home')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('studio')}
              className="hover:text-white transition-colors cursor-pointer text-[#6798ff]"
            >
              Navigation Studio
            </button>
            <button
              onClick={() => setActiveTab('registry')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Audit Registry ({scanHistory.length})
            </button>
            <button
              onClick={() => setIsGuideOpen(true)}
              className="hover:text-white transition-colors cursor-pointer"
            >
              Taxonomy Rubric
            </button>
          </div>
        </div>
      </footer>

      {/* Evidence Drilldown Modal */}
      {isEvidenceModalOpen && selectedScanData && (
        <EvidenceModal
          scanData={selectedScanData}
          onClose={() => setIsEvidenceModalOpen(false)}
          onOpenRegulatoryDossier={handleOpenDossier}
        />
      )}

      {/* Interactive Sandboxes */}
      {isSandboxOpen && (
        <SandboxSimulator
          onClose={() => setIsSandboxOpen(false)}
          onLaunchAudit={handleQuickScan}
        />
      )}

      {/* Detection Taxonomy Rubric */}
      {isGuideOpen && (
        <DarkPatternGuide
          onClose={() => setIsGuideOpen(false)}
        />
      )}

      {/* Regulatory Dossier Export Modal */}
      {isDossierOpen && dossierData && (
        <RegulatoryReportModal
          siteData={{
            site: {
              name: dossierData.site_name || dossierData.domain,
              domain: dossierData.domain,
              manipulation_index: dossierData.score_summary?.manipulation_index || 0,
              grade: dossierData.score_summary?.grade || 'N/A',
              ftc_risk_level: dossierData.score_summary?.ftc_risk_level || 'Critical Liability'
            },
            findings: dossierData.findings || []
          }}
          onClose={() => setIsDossierOpen(false)}
        />
      )}

      {/* AI Key Settings Modal */}
      {isApiKeyModalOpen && (
        <ApiKeyModal
          onClose={() => setIsApiKeyModalOpen(false)}
        />
      )}
    </div>
  );
}
