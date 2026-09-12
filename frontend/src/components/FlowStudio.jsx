import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, Play, Globe, Eye, Code, Scale, ShieldAlert, ArrowRight, 
  Layers, CheckCircle2, ChevronRight, RefreshCw, Loader2,
  ExternalLink, FileText, CornerDownRight, Check, AlertTriangle
} from 'lucide-react';
import { apiUrl } from '../lib/api';

export default function FlowStudio({ 
  initialScanData, 
  initialParams,
  onScanComplete, 
  onOpenDossier 
}) {
  const [targetUrl, setTargetUrl] = useState('http://127.0.0.1:8000/mock/shopsneak');
  const [siteName, setSiteName] = useState('ShopSneak Store');
  const [flowType, setFlowType] = useState('checkout');
  const [maxSteps, setMaxSteps] = useState(4);

  const [isScanning, setIsScanning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [activeNodeIndex, setActiveNodeIndex] = useState(0);
  
  // Real-time navigation nodes structure
  const [navigationNodes, setNavigationNodes] = useState(() => {
    return initialScanData?.navigation_nodes || initialScanData?.steps || [];
  });
  const [scanResult, setScanResult] = useState(initialScanData || null);

  const logsEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const presets = [
    { name: "ShopSneak Checkout", url: "http://127.0.0.1:8000/mock/shopsneak", flow: "checkout", steps: 4 },
    { name: "GymTrap Cancellation Maze", url: "http://127.0.0.1:8000/mock/gymtrap", flow: "cancellation", steps: 6 },
    { name: "McAfee AntiVirus Direct", url: "https://www.mcafee.com", flow: "checkout" },
    { name: "Hacker News (Clean Baseline)", url: "https://news.ycombinator.com", flow: "general" }
  ];

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  useEffect(() => {
    if (initialScanData) {
      setScanResult(initialScanData);
      setNavigationNodes(initialScanData.navigation_nodes || initialScanData.steps || []);
      setActiveNodeIndex(0);
    }
  }, [initialScanData]);

  useEffect(() => {
    if (initialParams && !isScanning) {
      setTargetUrl(initialParams.url || '');
      setSiteName(initialParams.name || 'Target Website');
      setFlowType(initialParams.flow || 'checkout');
      setMaxSteps(initialParams.flow === 'cancellation' ? 6 : 4);
    }
  }, [initialParams, isScanning]);

  useEffect(() => () => abortControllerRef.current?.abort(), []);

  const handleStartAudit = async () => {
    setIsScanning(true);
    setLogs([]);
    setNavigationNodes([]);
    setScanResult(null);
    setActiveNodeIndex(0);

    const apiKey = localStorage.getItem('pattern_guard_ai_key') || '';
    const aiEndpoint = localStorage.getItem('pattern_guard_ai_endpoint') || '';
    const aiModel = localStorage.getItem('pattern_guard_ai_model') || '';
    const brightDataUrl = localStorage.getItem('pattern_guard_brightdata_url') || '';
    const scanToken = localStorage.getItem('pattern_guard_scan_token') || '';
    const controller = new AbortController();
    abortControllerRef.current = controller;
    const addLog = (msg) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

    addLog(`INITIATING AUTONOMOUS NAVIGATION HARNESS: ${targetUrl}`);
    addLog(`SPAWNING HEADLESS CHROMIUM ENGINE WITH HTTP/2 PROTOCOL RESILIENCE...`);
    if (apiKey.trim()) {
      addLog(`AI INFERENCE LAYER: ACTIVE (Dynamic Model Resolver Enabled)`);
    } else {
      addLog(`DETERMINISTIC HEURISTICS: ACTIVE (DOM Attribute Parsing & Contrast Math)`);
    }

    try {
      const response = await fetch(apiUrl('/api/scan/stream'), {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(scanToken.trim() ? { 'X-Pattern-Guard-Token': scanToken.trim() } : {})
        },
        body: JSON.stringify({
          target_url: targetUrl,
          site_name: siteName,
          flow_type: flowType,
          max_steps: Number(maxSteps),
          ai_api_key: apiKey.trim() || undefined,
          ai_endpoint: aiEndpoint.trim() || undefined,
          ai_model: aiModel.trim() || undefined,
          bright_data_wss_url: brightDataUrl.trim() || undefined
        })
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(`Scan request failed (${response.status}): ${message.slice(0, 300)}`);
      }
      if (!response.body) throw new Error('Streaming response body is unavailable.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.replace('data: ', '').trim());
              
              if (data.event === 'log') {
                addLog(data.message);
              } else if (data.event === 'step_started') {
                addLog(`DISCOVERED NODE #${data.step_number}: '${data.title}'`);
              } else if (data.event === 'step_completed') {
                if (data.node_data) {
                  setNavigationNodes(prev => [...prev, data.node_data]);
                }
              } else if (data.event === 'finding_detected') {
                addLog(`VIOLATION FLAGGED: [${data.severity}] ${data.pattern_name} (+${data.score_impact} pts)`);
              } else if (data.event === 'scan_completed') {
                setScanResult(data);
                setNavigationNodes(data.navigation_nodes || data.steps || []);
                if (onScanComplete) {
                  onScanComplete(data);
                }
              } else if (data.event === 'error') {
                addLog(`[ERROR]: ${data.message}`);
              } else if (data.event === 'stream_end') {
                break;
              }
            } catch (err) {
              console.error('Error parsing SSE event:', err);
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') addLog(`HARNESS ERROR: ${err.message}`);
    } finally {
      abortControllerRef.current = null;
      setIsScanning(false);
    }
  };

  const currentNode = navigationNodes[activeNodeIndex] || null;
  const auditBlocked = scanResult?.audit_status === 'human_review_required';
  const nodeBlocked = currentNode?.audit_status === 'human_review_required';

  return (
    <div className="w-full min-h-[calc(100vh-56px)] bg-[#0a0a0a] text-white p-4 sm:p-8 font-sans">
      <div className="max-w-[1400px] mx-auto space-y-6">
        
        {/* Page Top Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1e1e1e]">
          <div>
            <div className="flex items-center gap-2 text-[12px] font-mono text-[#a7a7a7] uppercase tracking-[0.85px] mb-1">
              <span className="w-2 h-2 rounded-full bg-[#6798ff] animate-pulse"></span>
              <span>Autonomous Flow Studio & Navigation Harness</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-white">
              Website Funnel Navigation & Deception Analyzer
            </h1>
            <p className="text-[13px] text-[#a7a7a7] mt-0.5">
              Live crawler session that maps the entire funnel architecture, button decision paths, and deceptive choice mechanisms.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {scanResult && (
              <button
                onClick={() => onOpenDossier(scanResult)}
                className="bg-[#1e1e1e] hover:bg-[#282828] text-white border border-[#313131] px-3 py-1.5 rounded-[6px] text-[12px] font-mono flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <FileText className="w-3.5 h-3.5 text-[#6798ff]" />
                <span>Export Dossier</span>
              </button>
            )}
          </div>
        </div>

        {/* Audit Session Setup Bar */}
        <div className="p-4 sm:p-5 rounded-[8px] bg-[#141414] border border-[#1e1e1e] shadow-xl grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          <div className="md:col-span-6">
            <label className="block text-[11px] font-mono uppercase text-[#7c7c7c] mb-1.5">Target Website / Funnel URL</label>
            <div className="flex items-center rounded-[6px] bg-[#0a0a0a] border border-[#313131] focus-within:border-[#6798ff] px-3 py-1.5">
              <Globe className="w-4 h-4 text-[#7c7c7c] mr-2 shrink-0" />
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                disabled={isScanning}
                placeholder="https://..."
                className="w-full bg-transparent text-[13px] text-white font-mono placeholder:text-[#555] focus:outline-none"
              />
            </div>
          </div>

          <div className="md:col-span-3">
            <label className="block text-[11px] font-mono uppercase text-[#7c7c7c] mb-1.5">Flow Strategy</label>
            <select
              value={flowType}
              onChange={(e) => setFlowType(e.target.value)}
              disabled={isScanning}
              className="w-full bg-[#0a0a0a] border border-[#313131] rounded-[6px] px-3 py-2 text-[13px] text-white font-mono focus:outline-none focus:border-[#6798ff]"
            >
              <option value="checkout">Checkout & Upsell Funnel</option>
              <option value="cancellation">Cancellation Obstacle Maze</option>
              <option value="signup">1-Click Signup & Subscription</option>
              <option value="general">Comprehensive General Scan</option>
            </select>
          </div>

          <div className="md:col-span-3 pt-2 md:pt-0">
            <button
              onClick={handleStartAudit}
              disabled={isScanning}
              className={`w-full py-2.5 px-4 rounded-[6px] text-[13px] font-medium tracking-tight flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm ${
                isScanning
                  ? 'bg-zinc-800 text-zinc-400 cursor-not-allowed'
                  : 'bg-white hover:bg-zinc-200 text-[#0a0a0a]'
              }`}
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#6798ff]" />
                  <span>Auditing Structure ({navigationNodes.length} Nodes)...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Full Audit Harness</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Presets */}
          <div className="md:col-span-12 flex flex-wrap items-center gap-2 pt-1 border-t border-[#1e1e1e]/60 text-[11px] font-mono">
            <span className="text-[#7c7c7c]">PRESETS:</span>
            {presets.map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setTargetUrl(p.url);
                  setSiteName(p.name);
                  setFlowType(p.flow);
                  setMaxSteps(p.steps || 4);
                }}
                disabled={isScanning}
                className="px-2.5 py-0.5 rounded-[4px] bg-[#0a0a0a] hover:bg-[#1e1e1e] border border-[#1e1e1e] text-[#a7a7a7] hover:text-white transition-colors cursor-pointer"
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Step Navigation Flow Tree (Visual Node Graph) */}
        {navigationNodes.length > 0 && (
          <div className="p-5 rounded-[8px] bg-[#141414] border border-[#1e1e1e] space-y-3">
            <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#7c7c7c]">
              <span>Funnel Navigation Structure ({navigationNodes.length} Steps Traversed)</span>
              <span>Click node to inspect DOM & legal evidence</span>
            </div>

            <div className="flex items-center gap-3 overflow-x-auto pb-2">
              {navigationNodes.map((node, idx) => {
                const isActive = activeNodeIndex === idx;
                const findingsCount = node.findings?.length || node.findings_count || 0;
                return (
                  <div key={idx} className="flex items-center gap-3 shrink-0">
                    <button
                      onClick={() => setActiveNodeIndex(idx)}
                      className={`p-3.5 rounded-[6px] border text-left min-w-[220px] transition-all cursor-pointer flex flex-col justify-between ${
                        isActive
                          ? 'bg-[#1e1e1e] border-[#6798ff] shadow-lg ring-1 ring-[#6798ff]/30'
                          : 'bg-[#0a0a0a] border-[#1e1e1e] hover:border-[#313131]'
                      }`}
                    >
                      <div className="flex items-center justify-between font-mono text-[10px] mb-1">
                        <span className={isActive ? 'text-[#6798ff] font-bold' : 'text-[#7c7c7c]'}>
                          STEP 0{node.step_number || idx + 1}
                        </span>
                        <span className={`px-1.5 py-0.2 rounded-[3px] text-[9px] ${
                          findingsCount > 0 ? 'bg-[#ff6b6b]/10 text-[#ff6b6b] border border-[#ff6b6b]/30' : 'bg-[#51cf66]/10 text-[#51cf66]'
                        }`}>
                          {findingsCount} {findingsCount === 1 ? 'VIOLATION' : 'VIOLATIONS'}
                        </span>
                      </div>

                      <div className="text-[13px] font-medium text-white truncate max-w-[200px]">
                        {node.title || `Step ${idx + 1}`}
                      </div>

                      <div className="text-[10px] font-mono text-[#7c7c7c] truncate mt-1">
                        {node.url ? new URL(node.url).pathname || '/' : '/'}
                      </div>
                    </button>

                    {idx < navigationNodes.length - 1 && (
                      <div className="flex flex-col items-center justify-center text-[#7c7c7c]">
                        <ArrowRight className="w-4 h-4 text-[#6798ff]" />
                        <span className="text-[9px] font-mono uppercase text-[#555]">Transit</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Inspection Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Visual Screenshot & DOM Elements Tree (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            
            {/* Viewport Canvas */}
            <div className="border border-[#1e1e1e] rounded-[8px] bg-[#141414] overflow-hidden shadow-2xl">
              <div className="bg-[#0f0f0f] px-4 py-2.5 border-b border-[#1e1e1e] flex items-center justify-between text-[11px] font-mono">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1">
                    <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]"></div>
                  </div>
                  <span className="text-[#a7a7a7] ml-2">
                    {currentNode ? `Step ${currentNode.step_number}: ${currentNode.title}` : 'Headless Viewport (1280x800)'}
                  </span>
                </div>
                {currentNode && (
                  <span className="text-[#6798ff]">Active Node Proof</span>
                )}
              </div>

              <div className="p-4 bg-[#0a0a0a] flex items-center justify-center min-h-[360px]">
                {currentNode && (currentNode.annotated_screenshot || currentNode.raw_screenshot) ? (
                  <div className="w-full flex flex-col items-center">
                    <img
                      src={apiUrl(currentNode.annotated_screenshot || currentNode.raw_screenshot)}
                      alt="Step Viewport"
                      className="w-full h-auto max-h-[420px] object-contain rounded-[4px] border border-[#1e1e1e] bg-white shadow-md"
                    />
                  </div>
                ) : (
                  <div className="text-center p-12 space-y-3">
                    <Globe className="w-10 h-10 text-[#333] mx-auto" />
                    <div className="text-[13px] text-[#7c7c7c] font-mono">
                      Execute audit harness above to begin live full-funnel walkthrough.
                    </div>
                  </div>
                )}
              </div>

              {currentNode && (
                <div className="p-3 bg-[#0f0f0f] border-t border-[#1e1e1e] text-[11px] font-mono flex items-center justify-between text-[#a7a7a7]">
                  <span className="truncate max-w-md">Target: {currentNode.url}</span>
                  <span className="text-[#6798ff]">Intent: {currentNode.navigation_intent || 'Funnel Evaluation'}</span>
                </div>
              )}
            </div>

            {/* Deep DOM Architecture Inspector */}
            {currentNode && (
              <div className="p-5 rounded-[8px] bg-[#141414] border border-[#1e1e1e] space-y-4">
                <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#7c7c7c]">
                  <span>DOM Choice Architecture Structure</span>
                  <span>{currentNode.buttons?.length || 0} Interactive CTAs Discovered</span>
                </div>

                {/* Checkboxes (Pre-selected bias inspection) */}
                {currentNode.checkboxes && currentNode.checkboxes.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] font-mono text-[#6798ff] uppercase block">Checkboxes & Sneaked Options:</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {currentNode.checkboxes.map((cb, i) => (
                        <div key={i} className={`p-2.5 rounded-[4px] border text-[11px] font-mono flex items-center justify-between ${
                          cb.checked ? 'bg-[#ff6b6b]/10 border-[#ff6b6b]/30 text-white' : 'bg-[#0a0a0a] border-[#1e1e1e] text-[#a7a7a7]'
                        }`}>
                          <div className="truncate mr-2">
                            <span>{cb.label || 'Opt-in Checkbox'}</span>
                          </div>
                          <span className={`px-1.5 py-0.2 rounded-[2px] text-[9px] uppercase ${
                            cb.checked ? 'bg-[#ff6b6b] text-black font-bold' : 'bg-[#1e1e1e] text-[#7c7c7c]'
                          }`}>
                            {cb.checked ? 'PRE-CHECKED' : 'UNCHECKED'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Buttons & Navigation Targets */}
                {currentNode.buttons && currentNode.buttons.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[10px] font-mono text-[#a7a7a7] uppercase block">Discovered Call-to-Action Paths:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {currentNode.buttons.map((btn, i) => (
                        <span key={i} className="px-2.5 py-1 rounded-[4px] bg-[#0a0a0a] border border-[#1e1e1e] text-[11px] font-mono text-white flex items-center gap-1">
                          <Code className="w-3 h-3 text-[#6798ff]" />
                          <span>{btn.text}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Disclaimers & Fine Print */}
                {currentNode.disclaimers && currentNode.disclaimers.length > 0 && (
                  <div className="space-y-2 border-t border-[#1e1e1e] pt-3">
                    <span className="text-[10px] font-mono text-[#ffa94d] uppercase block">Low-Contrast / Camouflaged Disclaimers:</span>
                    <div className="space-y-1">
                      {currentNode.disclaimers.map((disc, i) => (
                        <div key={i} className="p-2 rounded-[4px] bg-[#0a0a0a] border border-[#1e1e1e] text-[11px] text-[#888] font-mono">
                          "{disc.text}" · <span className="text-[#ffa94d]">Size: {disc.fontSize}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>

          {/* Right Column: Violations Feed & Console Stream (5 Cols) */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Step Specific Violations Feed */}
            <div className="p-5 rounded-[8px] bg-[#141414] border border-[#1e1e1e] space-y-3 shadow-xl">
              <div className="flex items-center justify-between text-[11px] font-mono uppercase text-[#7c7c7c]">
                <span>Active Step Violations ({currentNode?.findings?.length || 0})</span>
                <span className={nodeBlocked ? 'text-[#ffa94d]' : (currentNode?.findings?.length || 0) > 0 ? 'text-[#ff6b6b]' : 'text-[#51cf66]'}>
                  {nodeBlocked ? 'Human Review Required' : (currentNode?.findings?.length || 0) > 0 ? 'Dark Patterns Detected' : 'Compliant Step'}
                </span>
              </div>

              <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                {nodeBlocked ? (
                  <div className="p-4 rounded-[6px] border border-[#ffa94d]/30 bg-[#ffa94d]/10 text-center text-[12px] text-[#ffd0a3]">
                    {currentNode.human_review_reason || 'Protected access challenge detected. This is not a compliance result.'}
                  </div>
                ) : (!currentNode?.findings || currentNode.findings.length === 0) ? (
                  <div className="p-4 rounded-[6px] border border-[#1e1e1e] bg-[#0a0a0a] text-center text-[12px] text-[#555] italic">
                    No deceptive patterns detected on this step node.
                  </div>
                ) : (
                  currentNode.findings.map((f, i) => (
                    <div key={i} className="p-3 rounded-[6px] border border-[#313131] bg-[#0a0a0a] text-[12px] space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-white">{f.pattern_name}</span>
                        <span className="text-[#ff6b6b] font-mono text-[10px]">+{f.score_impact} pts</span>
                      </div>
                      <p className="text-[11px] text-[#a7a7a7] leading-relaxed">
                        {f.plain_explanation}
                      </p>
                      {f.psychological_mechanism && (
                        <div className="text-[10px] font-mono text-[#ffa94d] bg-[#ffa94d]/10 px-2 py-0.5 rounded-[3px] border border-[#ffa94d]/20">
                          Cognitive Bias: {f.psychological_mechanism}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Live Telemetry & Console Log */}
            <div className="p-5 rounded-[8px] bg-[#141414] border border-[#1e1e1e] space-y-2 shadow-xl">
              <div className="text-[11px] font-mono uppercase text-[#7c7c7c] flex items-center justify-between">
                <span>Harness Console Telemetry</span>
                <span className="text-[#6798ff]">Real-Time SSE</span>
              </div>
              <div className="border border-[#1e1e1e] rounded-[6px] bg-[#0a0a0a] p-3 font-mono text-[11px] space-y-1 h-[200px] overflow-y-auto">
                {logs.length === 0 ? (
                  <div className="text-[#555] italic">Start audit to view live browser & AI thoughts.</div>
                ) : (
                  logs.map((line, i) => (
                    <div key={i} className="text-[#a7a7a7] leading-tight">
                      <span className="text-[#6798ff] mr-1">❯</span> {line}
                    </div>
                  ))
                )}
                <div ref={logsEndRef} />
              </div>
            </div>

            {/* Final Manipulation Index Summary Banner */}
            {scanResult && (
              <div className="p-4 rounded-[8px] border border-[#313131] bg-[#141414] text-white flex items-center justify-between shadow-2xl">
                <div>
                  {auditBlocked ? <>
                    <div className="font-mono text-[13px] text-[#ffa94d] font-bold uppercase">Audit blocked — human review required</div>
                    <div className="text-[11px] text-[#ffd0a3] font-mono mt-0.5">No compliance score was issued because the target returned a verification challenge.</div>
                  </> : <>
                    <div className="font-mono text-[13px] text-[#6798ff] font-bold uppercase">
                      Manipulation Index: {scanResult.score_summary.manipulation_index}/100 [GRADE {scanResult.score_summary.grade}]
                    </div>
                    <div className="text-[11px] text-[#a7a7a7] font-mono mt-0.5">
                      {scanResult.findings.length} Total Violations Flagged · {scanResult.duration_ms}ms Run Time
                    </div>
                  </>}
                </div>
                <button
                  onClick={() => onOpenDossier(scanResult)}
                  className="bg-white text-black hover:bg-zinc-200 px-3.5 py-1.5 rounded-[4px] text-[12px] font-medium transition-all cursor-pointer shadow-sm"
                >
                  Dossier →
                </button>
              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
}

