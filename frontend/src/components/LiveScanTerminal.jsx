import React, { useState, useEffect, useRef } from 'react';
import { X, Play, Terminal, AlertCircle, Loader2, Sparkles, Globe, Eye, CheckCircle2, ChevronRight } from 'lucide-react';

export default function LiveScanTerminal({ onClose, onScanComplete, initialUrl, initialName, initialFlow }) {
  const [targetUrl, setTargetUrl] = useState(initialUrl || 'http://127.0.0.1:8000/mock/shopsneak');
  const [siteName, setSiteName] = useState(initialName || 'ShopSneak Store');
  const [flowType, setFlowType] = useState(initialFlow || 'checkout');
  
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('pattern_guard_ai_key') || '');
  const [showAiInput, setShowAiInput] = useState(false);

  const [isScanning, setIsScanning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [liveScreenshot, setLiveScreenshot] = useState(null);
  const [currentStepInfo, setCurrentStepInfo] = useState(null);
  const [liveFindings, setLiveFindings] = useState([]);
  const [scanResult, setScanResult] = useState(null);

  const logsEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  const presets = [
    { name: "ShopSneak Checkout", url: "http://127.0.0.1:8000/mock/shopsneak", flow: "checkout" },
    { name: "GymTrap Cancellation", url: "http://127.0.0.1:8000/mock/gymtrap", flow: "cancellation" },
    { name: "Hacker News (Clean)", url: "https://news.ycombinator.com", flow: "general" }
  ];

  useEffect(() => {
    const freshKey = localStorage.getItem('pattern_guard_ai_key') || '';
    setApiKey(freshKey);
  }, []);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  useEffect(() => () => abortControllerRef.current?.abort(), []);

  const handleRunScan = async () => {
    setIsScanning(true);
    setLogs([]);
    setLiveFindings([]);
    setLiveScreenshot(null);
    setCurrentStepInfo(null);
    setScanResult(null);

    const addLog = (msg) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
    const controller = new AbortController();
    abortControllerRef.current = controller;

    addLog(`INITIATING AUTONOMOUS AGENT FOR: ${targetUrl}`);
    addLog(`SPAWNING HEADLESS CHROMIUM BROWSER...`);
    if (apiKey.trim()) {
      addLog(`AI INFERENCE LAYER: ACTIVE`);
    } else {
      addLog(`DEFAULT ENGINE: DETERMINISTIC DOM PARSING ACTIVE`);
    }

    try {
      const response = await fetch('/api/scan/stream', {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(localStorage.getItem('pattern_guard_scan_token') ? { 'X-Pattern-Guard-Token': localStorage.getItem('pattern_guard_scan_token') } : {})
        },
        body: JSON.stringify({
          target_url: targetUrl,
          site_name: siteName,
          flow_type: flowType,
          max_steps: 4,
          ai_api_key: apiKey.trim() || undefined,
          ai_endpoint: localStorage.getItem('pattern_guard_ai_endpoint') || undefined,
          ai_model: localStorage.getItem('pattern_guard_ai_model') || undefined,
          bright_data_wss_url: localStorage.getItem('pattern_guard_brightdata_url') || undefined
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
                setCurrentStepInfo({
                  step: data.step_number,
                  title: data.title,
                  url: data.url
                });
                if (data.screenshot_url) {
                  setLiveScreenshot(data.screenshot_url);
                }
              } else if (data.event === 'step_completed') {
                if (data.annotated_screenshot) {
                  setLiveScreenshot(data.annotated_screenshot);
                }
              } else if (data.event === 'finding_detected') {
                setLiveFindings(prev => [...prev, data]);
                addLog(`VIOLATION FLAGGED: [${data.severity}] ${data.pattern_name} (+${data.score_impact} pts)`);
              } else if (data.event === 'scan_completed') {
                setScanResult(data);
                if (onScanComplete) {
                  onScanComplete(data);
                }
              } else if (data.event === 'error') {
                addLog(`[ERROR]: ${data.message}`);
              } else if (data.event === 'stream_end') {
                break;
              }
            } catch (err) {
              console.error('Error parsing SSE data:', err);
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') addLog(`CRAWLER AGENT ERROR: ${err.message}`);
    } finally {
      abortControllerRef.current = null;
      setIsScanning(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-3 sm:p-6 backdrop-blur-md font-sans">
      <div className="bg-[#141414] border border-[#1e1e1e] w-full max-w-5xl max-h-[92vh] rounded-[8px] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#1e1e1e] bg-[#141414] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-[6px] bg-[#1e1e1e] border border-[#313131] flex items-center justify-center text-[#6798ff] font-mono text-xs">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium text-[15px] text-white">Autonomous Flow Auditor</span>
                {isScanning && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-[4px] text-[10px] font-mono bg-[#6798ff]/10 text-[#6798ff] border border-[#6798ff]/20 animate-pulse">
                    Scanning
                  </span>
                )}
              </div>
              <p className="text-[12px] text-[#7c7c7c] font-mono">Live headless traversal & dark pattern detection</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAiInput(!showAiInput)}
              className="px-2.5 py-1 rounded-[6px] bg-[#1e1e1e] hover:bg-[#282828] border border-[#313131] text-[12px] font-mono text-[#a7a7a7] hover:text-white transition-colors cursor-pointer"
            >
              {apiKey ? 'AI Active' : '+ AI Key'}
            </button>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-[4px] hover:bg-white/10 text-[#a7a7a7] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* AI Key Inline Drawer */}
        {showAiInput && (
          <div className="p-3.5 bg-[#0a0a0a] border-b border-[#1e1e1e] flex flex-col sm:flex-row items-center justify-between gap-3 text-[12px]">
            <span className="text-[#a7a7a7]">Optional AI API Key (Groq, OpenAI, etc.):</span>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="password"
                placeholder="gsk_... or sk-..."
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  localStorage.setItem('pattern_guard_ai_key', e.target.value);
                }}
                className="bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-1.5 text-white font-mono text-[12px] focus:outline-none focus:border-[#6798ff] w-full sm:w-64"
              />
              <button
                onClick={() => setShowAiInput(false)}
                className="bg-white text-black px-3 py-1.5 rounded-[6px] text-[12px] font-medium shrink-0 cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        )}

        {/* Action Bar */}
        <div className="p-4 bg-[#0f0f0f] border-b border-[#1e1e1e] grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          <div className="md:col-span-6">
            <label className="block text-[11px] font-mono uppercase text-[#7c7c7c] mb-1">Target Funnel URL</label>
            <div className="flex items-center rounded-[6px] bg-[#0a0a0a] border border-[#313131] focus-within:border-[#6798ff]">
              <div className="pl-3 pr-2 text-[#7c7c7c]">
                <Globe className="w-3.5 h-3.5" />
              </div>
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                disabled={isScanning}
                placeholder="https://..."
                className="w-full bg-transparent text-[13px] text-white font-mono placeholder:text-[#555] focus:outline-none py-1.5 pr-3"
              />
            </div>
          </div>

          <div className="md:col-span-3">
            <label className="block text-[11px] font-mono uppercase text-[#7c7c7c] mb-1">Strategy</label>
            <select
              value={flowType}
              onChange={(e) => setFlowType(e.target.value)}
              disabled={isScanning}
              className="w-full bg-[#0a0a0a] border border-[#313131] rounded-[6px] px-3 py-2 text-[13px] text-white font-mono focus:outline-none focus:border-[#6798ff]"
            >
              <option value="checkout">Checkout Funnel</option>
              <option value="cancellation">Cancellation Maze</option>
              <option value="signup">1-Click Signup</option>
              <option value="general">General Page</option>
            </select>
          </div>

          <div className="md:col-span-3 pt-3 md:pt-0">
            <button
              onClick={handleRunScan}
              disabled={isScanning}
              className={`w-full py-2 px-4 rounded-[6px] text-[13px] font-medium tracking-tight flex items-center justify-center gap-2 transition-all cursor-pointer ${
                isScanning
                  ? 'bg-zinc-800 text-zinc-400 cursor-not-allowed'
                  : 'bg-white hover:bg-zinc-200 text-[#0a0a0a]'
              }`}
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Auditing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Start Audit</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Visualizer Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 grid grid-cols-1 lg:grid-cols-12 gap-5">
          
          {/* Left: Viewport */}
          <div className="lg:col-span-7 flex flex-col space-y-2">
            <div className="border border-[#1e1e1e] rounded-[8px] bg-[#0a0a0a] overflow-hidden flex flex-col min-h-[340px]">
              
              {/* Browser Header */}
              <div className="bg-[#141414] px-3.5 py-2 border-b border-[#1e1e1e] flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-[#ff5f56]"></div>
                  <div className="w-2 h-2 rounded-full bg-[#ffbd2e]"></div>
                  <div className="w-2 h-2 rounded-full bg-[#27c93f]"></div>
                  <span className="text-[11px] font-mono text-[#a7a7a7] ml-2">
                    {currentStepInfo ? `Step ${currentStepInfo.step}: ${currentStepInfo.title}` : 'Headless Viewport (1280x800)'}
                  </span>
                </div>
              </div>

              {/* Viewport Content */}
              <div className="flex-1 p-2 flex items-center justify-center bg-[#0a0a0a] min-h-[280px]">
                {liveScreenshot ? (
                  <img
                    src={liveScreenshot}
                    alt="Live DOM Snapshot"
                    className="w-full h-auto max-h-[340px] object-contain rounded-[4px] border border-[#1e1e1e] bg-white"
                  />
                ) : (
                  <div className="text-center p-6 space-y-3">
                    <Globe className="w-8 h-8 text-[#454545] mx-auto" />
                    <div className="text-[12px] text-[#7c7c7c] font-mono">
                      Live page DOM renders here as the crawler traverses the website.
                    </div>
                    <div className="flex flex-wrap justify-center gap-2 pt-1">
                      {presets.map((p, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setTargetUrl(p.url);
                            setSiteName(p.name);
                            setFlowType(p.flow);
                          }}
                          className="text-[11px] font-mono px-2.5 py-1 rounded-[4px] bg-[#141414] border border-[#1e1e1e] text-[#a7a7a7] hover:text-white cursor-pointer"
                        >
                          {p.name}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {currentStepInfo && (
                <div className="px-3 py-1.5 bg-[#141414] border-t border-[#1e1e1e] text-[11px] font-mono text-[#a7a7a7] flex justify-between">
                  <span className="truncate max-w-sm">URL: {currentStepInfo.url}</span>
                  <span className="text-[#6798ff]">Step {currentStepInfo.step} Active</span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Findings & Console */}
          <div className="lg:col-span-5 flex flex-col space-y-4">
            
            {/* Findings Feed */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-mono text-[#a7a7a7] uppercase">
                <span>Flagged Patterns ({liveFindings.length})</span>
                <span className={liveFindings.length > 0 ? 'text-[#ff6b6b]' : 'text-[#7c7c7c]'}>
                  {liveFindings.length > 0 ? 'Violations Found' : 'Clean'}
                </span>
              </div>

              <div className="space-y-2 max-h-[140px] overflow-y-auto">
                {liveFindings.length === 0 ? (
                  <div className="p-3 rounded-[6px] border border-[#1e1e1e] bg-[#0a0a0a] text-center text-[12px] text-[#555] italic">
                    No dark patterns detected yet on current step.
                  </div>
                ) : (
                  liveFindings.map((f, i) => (
                    <div key={i} className="p-2.5 rounded-[6px] border border-[#313131] bg-[#141414] text-[12px] space-y-0.5">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-white">{f.pattern}</span>
                        <span className="text-[#ff6b6b] font-mono text-[10px]">+{f.score_impact} pts</span>
                      </div>
                      <p className="text-[11px] text-[#a7a7a7] leading-snug">{f.explanation}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Console Stream */}
            <div className="flex-1 flex flex-col space-y-1">
              <div className="text-[11px] font-mono text-[#7c7c7c] uppercase">Console Telemetry</div>
              <div className="border border-[#1e1e1e] rounded-[6px] bg-[#0a0a0a] p-3 font-mono text-[11px] space-y-1 h-[150px] overflow-y-auto">
                {logs.length === 0 ? (
                  <div className="text-[#555] italic">Click 'Start Audit' to begin crawler.</div>
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

            {/* Verdict */}
            {scanResult && (
              <div className="p-3.5 rounded-[6px] border border-[#313131] bg-[#141414] text-white flex items-center justify-between">
                <div>
                  <div className="font-mono text-[12px] text-[#6798ff] font-medium uppercase">
                    Audit Complete · Index: {scanResult.score_summary.manipulation_index}/100
                  </div>
                  <div className="text-[11px] text-[#a7a7a7] font-mono mt-0.5">
                    Grade: {scanResult.score_summary.grade} · {scanResult.findings.length} Violations
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="bg-white text-black px-3 py-1.5 rounded-[4px] text-[12px] font-medium cursor-pointer"
                >
                  View Details →
                </button>
              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
}
