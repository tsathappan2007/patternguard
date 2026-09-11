import React, { useState } from 'react';
import { X, Sparkles, Check, Globe, Shield, Zap } from 'lucide-react';

export default function ApiKeyModal({ onClose, onSaved }) {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('pattern_guard_ai_key') || '');
  const [brightDataUrl, setBrightDataUrl] = useState(() => localStorage.getItem('pattern_guard_brightdata_url') || '');
  const [aiEndpoint, setAiEndpoint] = useState(() => localStorage.getItem('pattern_guard_ai_endpoint') || '');
  const [aiModel, setAiModel] = useState(() => localStorage.getItem('pattern_guard_ai_model') || '');
  const [scanToken, setScanToken] = useState(() => localStorage.getItem('pattern_guard_scan_token') || '');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = () => {
    localStorage.setItem('pattern_guard_ai_key', apiKey.trim());
    localStorage.setItem('pattern_guard_brightdata_url', brightDataUrl.trim());
    localStorage.setItem('pattern_guard_ai_endpoint', aiEndpoint.trim());
    localStorage.setItem('pattern_guard_ai_model', aiModel.trim());
    localStorage.setItem('pattern_guard_scan_token', scanToken.trim());
    setSavedSuccess(true);
    if (onSaved) onSaved({ apiKey: apiKey.trim(), brightDataUrl: brightDataUrl.trim(), aiEndpoint: aiEndpoint.trim(), aiModel: aiModel.trim(), scanToken: scanToken.trim() });
    setTimeout(() => {
      onClose();
    }, 600);
  };

  const handleClear = () => {
    setApiKey('');
    setBrightDataUrl('');
    setAiEndpoint('');
    setAiModel('');
    setScanToken('');
    localStorage.removeItem('pattern_guard_ai_key');
    localStorage.removeItem('pattern_guard_brightdata_url');
    localStorage.removeItem('pattern_guard_ai_endpoint');
    localStorage.removeItem('pattern_guard_ai_model');
    localStorage.removeItem('pattern_guard_scan_token');
    setSavedSuccess(true);
    if (onSaved) onSaved({ apiKey: '', brightDataUrl: '', aiEndpoint: '', aiModel: '' });
    setTimeout(() => {
      onClose();
    }, 500);
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-md font-sans">
      <div className="bg-[#141414] border border-[#1e1e1e] w-full max-w-lg rounded-[8px] shadow-2xl overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="p-5 border-b border-[#1e1e1e] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-[6px] bg-[#1e1e1e] border border-[#313131] flex items-center justify-center text-[#6798ff]">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-[15px] font-medium text-white">Engine & Scraping Network Config</h3>
              <p className="text-[11px] text-[#7c7c7c] font-mono">Bright Data & AI Inference integration</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-[4px] hover:bg-white/10 flex items-center justify-center text-[#a7a7a7] hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 text-[13px] overflow-y-auto max-h-[70vh]">
          <div className="space-y-2 p-4 rounded-[6px] bg-[#0a0a0a] border border-[#1e1e1e]">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-[#51cf66]" />
              <span className="font-medium text-white text-[13px]">Server Scan Access</span>
            </div>
            <input
              type="password"
              placeholder="Optional X-Pattern-Guard-Token"
              value={scanToken}
              onChange={(e) => setScanToken(e.target.value)}
              className="w-full bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-2 text-[12px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] font-mono"
            />
          </div>
          
          {/* Bright Data Section */}
          <div className="space-y-2.5 p-4 rounded-[6px] bg-[#0a0a0a] border border-[#1e1e1e]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-[#6798ff]" />
                <span className="font-medium text-white text-[13px]">Bright Data Scraping Network</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-[3px] bg-[#6798ff]/10 text-[#6798ff] border border-[#6798ff]/30">
                Hackathon Sponsor
              </span>
            </div>

            <p className="text-[12px] text-[#a7a7a7] leading-relaxed">
              Provides CAPTCHA solving, residential proxies, and Cloudflare bypass for real-world sites.
            </p>

            <div className="space-y-1 pt-1">
              <label className="block text-[11px] font-mono uppercase text-[#7c7c7c]">
                Scraping Browser WebSocket URL
              </label>
              <input
                type="password"
                placeholder="wss://brd-customer-...:password@brd.superproxy.io:9222"
                value={brightDataUrl}
                onChange={(e) => setBrightDataUrl(e.target.value)}
                className="w-full bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-2 text-[12px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] font-mono"
              />
            </div>
            <div className="flex items-start gap-2 pt-1 text-[11px] text-[#51cf66]">
              <Shield className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <span>
                <strong>Smart Credit Saver Active</strong>: Localhost/mock tests use 0 credits; only live external sites route through Bright Data.
              </span>
            </div>
          </div>

          {/* AI Inference Section */}
          <div className="space-y-2.5 p-4 rounded-[6px] bg-[#0a0a0a] border border-[#1e1e1e]">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#ffd43b]" />
              <span className="font-medium text-white text-[13px]">AI Inference Layer (Optional)</span>
            </div>

            <p className="text-[12px] text-[#a7a7a7] leading-relaxed">
              Enables semantic cognitive bias classification via Groq (Llama 3.3), OpenAI, or xAI.
            </p>

            <div className="space-y-1 pt-1">
              <label className="block text-[11px] font-mono uppercase text-[#7c7c7c]">
                API Key (Groq, OpenAI, xAI)
              </label>
              <input
                type="password"
                placeholder="gsk_... or sk-..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-2 text-[12px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] font-mono"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              <div>
                <label className="block text-[10px] font-mono uppercase text-[#7c7c7c] mb-1">Custom API Base URL</label>
                <input
                  type="url"
                  placeholder="https://api.example.com/v1"
                  value={aiEndpoint}
                  onChange={(e) => setAiEndpoint(e.target.value)}
                  className="w-full bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-2 text-[11px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] font-mono"
                />
              </div>
              <div>
                <label className="block text-[10px] font-mono uppercase text-[#7c7c7c] mb-1">Model Override</label>
                <input
                  type="text"
                  placeholder="model-id"
                  value={aiModel}
                  onChange={(e) => setAiModel(e.target.value)}
                  className="w-full bg-[#141414] border border-[#313131] rounded-[6px] px-3 py-2 text-[11px] text-white placeholder:text-[#555] focus:outline-none focus:border-[#6798ff] font-mono"
                />
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#1e1e1e] bg-[#0f0f0f] flex items-center justify-between">
          <button
            type="button"
            onClick={handleClear}
            className="text-[12px] text-[#7c7c7c] hover:text-white transition-colors font-mono cursor-pointer"
          >
            Clear Credentials
          </button>
          
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-[6px] text-[13px] text-[#a7a7a7] hover:bg-white/5 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-4 py-1.5 rounded-[6px] text-[13px] font-medium transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
            >
              {savedSuccess ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Saved</span>
                </>
              ) : (
                <span>Save Configurations</span>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
