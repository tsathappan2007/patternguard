import React from 'react';
import { Play, Compass, Layers, Archive, BookOpen, ShieldCheck } from 'lucide-react';
import LogoComponent from './logo';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  onOpenScanner, 
  onOpenSandbox, 
  onOpenGuide, 
  scanCount = 0 
}) {
  return (
    <header className="w-full bg-[#0a0a0a]/90 backdrop-blur-md border-b border-[#1e1e1e] sticky top-0 z-40 font-sans">
      <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center justify-between">
        
        {/* Brand Logo & Navigation */}
        <div className="flex items-center gap-8">
          <div 
            className="flex items-center gap-2.5 cursor-pointer"
            onClick={() => setActiveTab('home')}
          >
            PATTERN GUARD
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-5 text-[13px] ">
            <button
              onClick={() => setActiveTab('home')}
              className={`transition-colors cursor-pointer ${
                activeTab === 'home' ? 'text-white font-medium' : 'text-[#a7a7a7] hover:text-white'
              }`}
            >
              Overview
            </button>

            <button
              onClick={() => setActiveTab('studio')}
              className={`transition-colors cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'studio' ? 'text-white font-medium' : 'text-[#a7a7a7] hover:text-white'
              }`}
            >
              <span>Navigation Studio</span>
              <span className="px-1.5 py-0.2 rounded-[4px] bg-[#6798ff]/20 text-[#6798ff] font-mono text-[9px]">
                HARNESS
              </span>
            </button>

            <button
              onClick={() => setActiveTab('registry')}
              className={`transition-colors cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'registry' ? 'text-white font-medium' : 'text-[#a7a7a7] hover:text-white'
              }`}
            >
              <span>Audit Registry</span>
              {scanCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-[4px] bg-[#6798ff]/20 text-[#6798ff] font-mono text-[10px]">
                  {scanCount}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('authority')}
              className={`transition-colors cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'authority' ? 'text-white font-medium' : 'text-[#a7a7a7] hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Authority Review</span>
            </button>

            <button 
              onClick={onOpenSandbox} 
              className="text-[#a7a7a7] hover:text-white transition-colors cursor-pointer"
            >
              Sandboxes
            </button>

            <button 
              onClick={onOpenGuide} 
              className="text-[#a7a7a7] hover:text-white transition-colors cursor-pointer"
            >
              Taxonomy Rubric
            </button>
          </nav>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          
          {/* Primary Action Button */}
          <button
            onClick={() => setActiveTab('studio')}
            className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-3.5 py-1.5 rounded-[6px] text-[13px] font-medium tracking-[-0.2px] transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
          >
            <Play className="w-3 h-3 fill-current" />
            <span>Launch Harness</span>
          </button>
        </div>

      </div>
    </header>
  );
}
