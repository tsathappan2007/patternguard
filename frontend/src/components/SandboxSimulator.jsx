import React, { useState } from 'react';
import { X, ExternalLink, Play, AlertTriangle, ArrowRight, RefreshCw, Check } from 'lucide-react';

export default function SandboxSimulator({ onClose, onLaunchAudit }) {
  const [activeTab, setActiveTab] = useState('shopsneak');

  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-3 sm:p-6 backdrop-blur-md">
      <div className="bg-[#121215] border border-white/10 w-full max-w-5xl max-h-[92vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-[#18181b]/60 flex items-center justify-between">
          <div>
            <div className="font-mono text-[10px] text-zinc-500 uppercase tracking-wider">
              Interactive Testgrounds
            </div>
            <h3 className="text-base font-semibold text-white">Deceptive Funnel Sandboxes</h3>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10 bg-[#141417] text-xs font-mono">
          <button
            onClick={() => setActiveTab('shopsneak')}
            className={`px-5 py-3 border-r border-white/10 transition-all cursor-pointer ${
              activeTab === 'shopsneak'
                ? 'bg-[#18181b] text-white font-semibold border-b-2 border-b-blue-500'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            1. ShopSneak (Checkout Drip & Pre-checked Warranty)
          </button>
          <button
            onClick={() => setActiveTab('gymtrap')}
            className={`px-5 py-3 border-r border-white/10 transition-all cursor-pointer ${
              activeTab === 'gymtrap'
                ? 'bg-[#18181b] text-white font-semibold border-b-2 border-b-blue-500'
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            2. GymTrap SaaS (4-Step Roach Motel Cancel)
          </button>
        </div>

        {/* Body Sandbox Viewer */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1">
          
          {activeTab === 'shopsneak' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-blue-950/20 border border-blue-500/20 p-4 rounded-xl gap-3">
                <div>
                  <h4 className="font-semibold text-sm text-blue-300">ShopSneak E-Commerce Funnel</h4>
                  <p className="text-xs text-blue-200/80 mt-0.5">
                    Includes pre-checked accidental warranty ($18.99), fake resetting 5-minute countdown clock, hidden convenience fee ($7.50), and camouflaged auto-renewal disclaimer.
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <a
                    href="http://127.0.0.1:8000/mock/shopsneak"
                    target="_blank"
                    rel="noreferrer"
                    className="bg-white/5 border border-white/10 text-zinc-300 px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 hover:bg-white/10"
                  >
                    <span>New Tab</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                  <button
                    onClick={() => onLaunchAudit('http://127.0.0.1:8000/mock/shopsneak', 'ShopSneak Store', 'checkout')}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 cursor-pointer"
                  >
                    <span>Audit with Pattern Guard →</span>
                  </button>
                </div>
              </div>

              {/* Embedded Iframe Simulator */}
              <div className="border border-white/10 rounded-xl bg-white h-[440px] overflow-hidden shadow-inner">
                <iframe
                  src="http://127.0.0.1:8000/mock/shopsneak"
                  title="ShopSneak Demo"
                  className="w-full h-full border-none"
                />
              </div>
            </div>
          )}

          {activeTab === 'gymtrap' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-red-950/20 border border-red-500/20 p-4 rounded-xl gap-3">
                <div>
                  <h4 className="font-semibold text-sm text-red-300">GymTrap SaaS Roach Motel Funnel</h4>
                  <p className="text-xs text-red-200/80 mt-0.5">
                    1-click instant signup vs grueling 4-page cancellation labyrinth, confirmshaming guilt-tripping ("Yes, delete all my progress forever"), and phone-call verification wall.
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <a
                    href="http://127.0.0.1:8000/mock/gymtrap"
                    target="_blank"
                    rel="noreferrer"
                    className="bg-white/5 border border-white/10 text-zinc-300 px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 hover:bg-white/10"
                  >
                    <span>New Tab</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                  <button
                    onClick={() => onLaunchAudit('http://127.0.0.1:8000/mock/gymtrap', 'GymTrap Elite SaaS', 'cancellation')}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1 cursor-pointer"
                  >
                    <span>Audit with Pattern Guard →</span>
                  </button>
                </div>
              </div>

              {/* Embedded Iframe Simulator */}
              <div className="border border-white/10 rounded-xl bg-white h-[440px] overflow-hidden shadow-inner">
                <iframe
                  src="http://127.0.0.1:8000/mock/gymtrap"
                  title="GymTrap Demo"
                  className="w-full h-full border-none"
                />
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
