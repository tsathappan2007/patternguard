import React, { useState } from 'react';
import { ArrowRight, Play, Shield, Globe, ChevronRight, Scale, Cpu, Eye, CheckCircle2, BarChart3, FileCheck } from 'lucide-react';
import LogoComponent from './logo';
import MangaBackground from './back';

export default function HeroBand({ onOpenScanner, onOpenSandbox, onQuickScan }) {
  const [quickUrl, setQuickUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (quickUrl.trim()) {
      onQuickScan(quickUrl.trim(), 'Target Website', 'checkout');
    } else {
      onOpenScanner();
    }
  };

  const capabilities = [
    {
      title: "Crawls live checkout & cancel paths",
      desc: "Our headless browser handles multi-step checkout sequences, cookie prompts, and hidden account termination loops automatically.",
      icon: Globe,
      tag: "FUNNEL NAVIGATION"
    },
    {
      title: "Catches late-stage price bumps",
      desc: "Flags unexpected service charges, forced add-ons, and bait-and-switch fees right before the final payment confirmation.",
      icon: Cpu,
      tag: "FEE INTERCEPTION"
    },
    {
      title: "Highlights deceptive elements in DOM",
      desc: "Pins exact bounding boxes onto misleading UI components and links them straight to their code selectors.",
      icon: Eye,
      tag: "DOM MAPPING"
    },
    {
      title: "Measures cancellation friction",
      desc: "Compares the ease of signing up in one click against the multi-page mazes required to cancel a subscription.",
      icon: Shield,
      tag: "ROACH MOTELS"
    },
    {
      title: "Flags manipulative button copy",
      desc: "Identifies confirmshaming, false countdown timers, and guilt-inducing language designed to force compliance.",
      icon: Scale,
      tag: "COPY ANALYSIS"
    },
    {
      title: "Generates regulatory reports",
      desc: "Exports clean evidence files mapped directly to FTC guidelines and consumer protection laws.",
      icon: FileCheck,
      tag: "COMPLIANCE EXPORTS"
    }
  ];

  return (
    <div className="relative w-full bg-[#0a0a0a] text-white overflow-hidden font-sans selection:bg-[#6798ff] selection:text-black">
      
      {/* Blueprint Grid Background Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e1e1e_1px,transparent_1px),linear-gradient(to_bottom,#1e1e1e_1px,transparent_1px)] bg-[size:48px_48px] opacity-[0.05] pointer-events-none z-0"></div>

      {/* 1. HERO SECTION - pt-0 touches the navbar */}
      <section className="relative pt-0 pb-32 px-6 flex flex-col items-center text-center mx-auto overflow-hidden">
        
        <MangaBackground>

          
          {/* Ambient Indigo Glow */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[250px] bg-[#6798ff]/10 rounded-full blur-[120px] pointer-events-none z-0"></div>

          {/* Foreground Content Stack */}
          <div className="relative z-10 flex flex-col items-center max-w-5xl mx-auto w-full">
            
            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-[64px] font-medium tracking-tight text-white max-w-5xl leading-[1.13] mb-6 mt-10">
              <div align="center" className='pt-24'><LogoComponent /></div>
              Identify dark patterns in website flows with precision.
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-[#a7a7a7] max-w-2xl leading-[1.5] mb-12">
              Houdini is an automated tool used to identify dark patterns in a website. It walks real signup, checkout, and cancellation funnels to detect manipulative UX in the act.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
              <button
                onClick={onOpenScanner}
                className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-5 py-2.5 rounded-[8px] text-[14px] font-medium tracking-[-0.25px] transition-all flex items-center gap-2 cursor-pointer shadow-sm"
              >
                <span>Audit Target Website</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              
              <button
                onClick={onOpenSandbox}
                className="bg-transparent hover:bg-white/5 text-white border border-[#454545] px-5 py-2.5 rounded-[8px] text-[14px] font-medium tracking-[-0.25px] transition-all flex items-center gap-2 cursor-pointer"
              >
                <span>Interactive Demo</span>
              </button>
            </div>

            {/* Quick URL Input Card */}
            <div className="w-full max-w-3xl mx-auto rounded-[8px] bg-[#141414]/95 backdrop-blur-md border border-[#1e1e1e] p-6 sm:p-8 text-left shadow-2xl relative z-20">
              
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1e1e1e]">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#6798ff] animate-pulse"></span>
                  <span className="font-mono text-[12px] uppercase text-[#a7a7a7] tracking-[0.85px]">LIVE INSPECTION TOOL</span>
                </div>
                <span className="font-mono text-[12px] text-[#7c7c7c]">v2.4.0</span>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-[14px] text-white font-medium mb-2">Target Funnel URL</label>
                  <div className="flex items-center p-1.5 rounded-[8px] bg-[#0a0a0a] border border-[#313131] focus-within:border-[#6798ff] transition-all">
                    <div className="pl-3 pr-2 text-[#7c7c7c]">
                      <Globe className="w-4 h-4" />
                    </div>
                    <input
                      type="text"
                      placeholder="https://target-store.com/checkout"
                      value={quickUrl}
                      onChange={(e) => setQuickUrl(e.target.value)}
                      className="flex-1 bg-transparent text-[14px] text-white placeholder:text-[#7c7c7c] focus:outline-none font-mono py-1.5"
                    />
                    <button
                      type="submit"
                      className="bg-[#6798ff] hover:bg-[#5282e6] text-[#0a0a0a] px-4 py-2 rounded-[6px] text-[14px] font-medium transition-all flex items-center gap-1.5 cursor-pointer"
                    >
                      <Play className="w-3 h-3 fill-current" />
                      <span>Scan</span>
                    </button>
                  </div>
                </div>
              </form>

              {/* Quick Presets */}
              <div className="flex flex-wrap items-center justify-between text-[12px] text-[#a7a7a7] pt-4 mt-4 border-t border-[#1e1e1e] font-mono">
                <span>QUICK PRESETS:</span>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => onQuickScan('http://127.0.0.1:8000/mock/shopsneak', 'ShopSneak Store', 'checkout')}
                    className="text-[#6798ff] hover:underline cursor-pointer"
                  >
                    ShopSneak Checkout
                  </button>
                  <span className="text-[#313131]">/</span>
                  <button
                    type="button"
                    onClick={() => onQuickScan('http://127.0.0.1:8000/mock/gymtrap', 'GymTrap Elite SaaS', 'cancellation')}
                    className="text-[#6798ff] hover:underline cursor-pointer"
                  >
                    GymTrap Cancellation
                  </button>
                </div>
              </div>

            </div>

            {/* Regulatory Strip */}
            <div className="w-full max-w-4xl mx-auto pt-20 border-t border-[#1e1e1e] mt-20 flex flex-col items-center">
              <span className="font-mono text-[12px] uppercase text-[#a7a7a7] tracking-[0.85px] mb-6">
                VERIFIED COMPLIANCE FRAMEWORKS
              </span>
              <div className="flex flex-wrap items-center justify-center gap-8 text-[12px] font-mono text-[#a7a7a7]">
                <span className="flex items-center gap-2"><Shield className="w-3.5 h-3.5 text-[#6798ff]" /> FTC ACT § 5</span>
                <span className="flex items-center gap-2"><Scale className="w-3.5 h-3.5 text-[#6798ff]" /> EU DSA ART. 25</span>
                <span className="flex items-center gap-2"><FileCheck className="w-3.5 h-3.5 text-[#6798ff]" /> CAL. SB 478</span>
                <span className="flex items-center gap-2"><Eye className="w-3.5 h-3.5 text-[#6798ff]" /> WCAG 2.1 AA</span>
              </div>
            </div>

          </div>
        </MangaBackground>
      </section>

      {/* 2. CAPABILITIES SECTION */}
      <section className="py-20 px-6 max-w-[1200px] mx-auto border-t border-[#1e1e1e]">
        <div className="max-w-2xl mb-16 space-y-3">
          <span className="font-mono text-[12px] uppercase text-[#a7a7a7] tracking-[0.85px]">
            CAPABILITIES
          </span>
          <h2 className="text-[40px] font-medium text-white tracking-[-0.84px] leading-[1.2]">
            How Houdini finds deceptive UX
          </h2>
          <p className="text-[16px] text-[#a7a7a7] leading-[1.5]">
            Practical features built to surface hidden traps in real-world user flows.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {capabilities.map((c, i) => {
            const Icon = c.icon;
            return (
              <div
                key={i}
                className="p-6 rounded-[8px] bg-[#141414] border border-[#1e1e1e] hover:border-[#313131] transition-all duration-200 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-10 h-10 rounded-[8px] bg-[#1e1e1e] border border-[#313131] flex items-center justify-center text-[#6798ff]">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="font-mono text-[12px] text-[#a7a7a7] bg-[#0a0a0a] px-2 py-0.5 rounded-[4px] border border-[#1e1e1e]">
                      {c.tag}
                    </span>
                  </div>
                  <h3 className="text-[20px] font-medium text-white tracking-[-0.42px] mb-2">{c.title}</h3>
                  <p className="text-[14px] text-[#a7a7a7] leading-[1.57]">{c.desc}</p>
                </div>

                <div className="pt-6 mt-6 border-t border-[#1e1e1e] flex items-center text-[14px] font-medium text-[#6798ff] group-hover:text-white transition-colors">
                  <span>Explore protocol</span>
                  <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. DASHBOARD PREVIEW & FORENSICS SECTION */}
      <section className="py-20 px-6 max-w-[1200px] mx-auto border-t border-[#1e1e1e]">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          <div className="lg:col-span-6 space-y-6">
            <span className="font-mono text-[12px] uppercase text-[#a7a7a7] tracking-[0.85px]">
              FORENSIC SIMULATION
            </span>
            <h2 className="text-[40px] font-medium text-white tracking-[-0.84px] leading-[1.2]">
              Proactive dark pattern testing before regulatory subpoenas
            </h2>
            <p className="text-[16px] text-[#a7a7a7] leading-[1.5]">
              Houdini actively challenges checkout carts, tests whether countdown clocks reset upon reload, and maps out hidden subscription fee escalation.
            </p>
            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-3 text-[14px] text-[#a7a7a7]">
                <CheckCircle2 className="w-4 h-4 text-[#6798ff] shrink-0" />
                <span>Automated detection of pre-selected checkboxes and hidden carts</span>
              </div>
              <div className="flex items-center gap-3 text-[14px] text-[#a7a7a7]">
                <CheckCircle2 className="w-4 h-4 text-[#6798ff] shrink-0" />
                <span>WCAG 2.1 AA luminance contrast verification on fine print disclaimers</span>
              </div>
            </div>
            <div className="pt-4">
              <button
                onClick={onOpenScanner}
                className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-5 py-2.5 rounded-[8px] text-[14px] font-medium transition-all flex items-center gap-2 cursor-pointer"
              >
                <span>Run Interactive Scan</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Dashboard Preview Card Mockup */}
          <div className="lg:col-span-6 p-6 rounded-[8px] bg-[#141414] border border-[#1e1e1e] shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-[#1e1e1e] pb-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#6798ff]" />
                <span className="font-mono text-[12px] text-white font-medium uppercase tracking-wider">CHECKOUT MANIPULATION INDEX</span>
              </div>
              <span className="font-mono text-[12px] text-[#ff6b6b] bg-[#ff6b6b]/10 px-2 py-0.5 rounded border border-[#ff6b6b]/30">+48.5 PTS</span>
            </div>

            <div className="space-y-4 font-mono text-[12px]">
              <div>
                <div className="flex justify-between text-[#a7a7a7] mb-1.5">
                  <span>Step 1: Product Selection</span>
                  <span className="text-white">$49.99 (Clean)</span>
                </div>
                <div className="w-full bg-[#0a0a0a] rounded-full h-2 overflow-hidden border border-[#313131]">
                  <div className="bg-[#6798ff] h-full w-[20%]"></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[#a7a7a7] mb-1.5">
                  <span>Step 2: Cart Add-ons (Sneaked Warranty)</span>
                  <span className="text-white">$68.98 (+38%)</span>
                </div>
                <div className="w-full bg-[#0a0a0a] rounded-full h-2 overflow-hidden border border-[#313131]">
                  <div className="bg-[#6798ff]/80 h-full w-[65%]"></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[#a7a7a7] mb-1.5">
                  <span>Step 3: Checkout Drip Fees</span>
                  <span className="text-[#ff6b6b]">$81.33 (+62.6%)</span>
                </div>
                <div className="w-full bg-[#0a0a0a] rounded-full h-2 overflow-hidden border border-[#313131]">
                  <div className="bg-[#ff6b6b] h-full w-[95%]"></div>
                </div>
              </div>
            </div>

            <div className="p-3.5 bg-[#0a0a0a] border border-[#313131] rounded-[8px] text-[12px] text-[#a7a7a7] font-mono leading-relaxed">
              <span className="text-[#ff6b6b] font-bold">VIOLATION DETECTED:</span> Final checkout total exceeds initial advertised price by $31.34 without prior conspicuous disclosure under FTC Act § 5.
            </div>
          </div>

        </div>
      </section>

      {/* 4. FOOTER CALL TO ACTION BANNER */}
      <section className="py-20 px-6 max-w-[1200px] mx-auto border-t border-[#1e1e1e]">
        <div className="rounded-[8px] bg-[#141414] border border-[#1e1e1e] p-10 sm:p-16 text-center space-y-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e1e1e_1px,transparent_1px),linear-gradient(to_bottom,#1e1e1e_1px,transparent_1px)] bg-[size:32px_32px] opacity-10 pointer-events-none"></div>

          <div className="relative z-10 max-w-2xl mx-auto space-y-4">
            <h2 className="text-[40px] font-medium text-white tracking-[-0.84px] leading-[1.2]">
              Strengthen Your Digital Compliance Today
            </h2>
            <p className="text-[16px] text-[#a7a7a7] leading-[1.5]">
              Deploy autonomous dark pattern testing across your web funnels to eliminate regulatory liability and build verified consumer trust.
            </p>
            <div className="pt-4">
              <button
                onClick={onOpenScanner}
                className="bg-white hover:bg-zinc-200 text-[#0a0a0a] px-6 py-3 rounded-[8px] text-[14px] font-medium transition-all shadow-sm inline-flex items-center gap-2 cursor-pointer"
              >
                <span>Audit Target Website Now</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}