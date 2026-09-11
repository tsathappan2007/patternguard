import React from 'react';

export default function LogoComponent({ size = 'md', glowingAura = false }) {
  const letters = [
    { char: 'P' },
    { char: 'A' },
    { char: 'T' },
    { char: 'T' },
    { char: 'E' },
    { char: 'R' },
    { char: 'N' },
    { char: 'G' },
    { char: 'U' },
    { char: 'A' },
    { char: 'R' },
    { char: 'D' }
  ];

  const centerIndex = Math.floor(letters.length / 2);

  const sizeConfig = {
    sm: {
      keycap: 'w-8 h-8 sm:w-10 sm:h-10',
      text: 'text-base sm:text-lg',
      inset: 'inset-[3px] sm:inset-[4px]',
      aura: 'w-20 h-20',
      star: 'w-16 h-16',
      starSmall: 'w-10 h-10',
      borderT: 'border-t-[6px]',
    },
    md: {
      keycap: 'w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20',
      text: 'text-xl sm:text-3xl md:text-4xl',
      inset: 'inset-[6px] sm:inset-[8px] md:inset-[10px]',
      aura: 'w-36 h-36',
      star: 'w-28 h-28',
      starSmall: 'w-16 h-16',
      borderT: 'border-t-[12px]',
    },
    lg: {
      keycap: 'w-16 h-16 sm:w-20 sm:h-20 md:w-28 md:h-28',
      text: 'text-2xl sm:text-4xl md:text-5xl',
      inset: 'inset-[8px] sm:inset-[10px] md:inset-[14px]',
      aura: 'w-48 h-48',
      star: 'w-40 h-40',
      starSmall: 'w-24 h-24',
      borderT: 'border-t-[16px]',
    },
    xl: {
      keycap: 'w-20 h-20 sm:w-28 sm:h-28 md:w-36 md:h-36',
      text: 'text-3xl sm:text-5xl md:text-7xl',
      inset: 'inset-[10px] sm:inset-[14px] md:inset-[18px]',
      aura: 'w-64 h-64',
      star: 'w-56 h-56',
      starSmall: 'w-32 h-32',
      borderT: 'border-t-[20px]',
    }
  };

  const currentSize = sizeConfig[size] || sizeConfig.md;

  return (
    <>
      <style>{`
        @keyframes autoPress {
          0%, 100% {
            transform: scale(1) translateY(0);
          }
          15% {
            transform: scale(0.95) translateY(4px);
          }
          30% {
            transform: scale(1) translateY(0);
          }
        }

        @keyframes cyberGlow {
          0%, 100% {
            opacity: 0;
            transform: scale(0.8);
          }
          15% {
            opacity: ${glowingAura ? '1' : '0'};
            transform: scale(1.15);
          }
          30% {
            opacity: 0;
            transform: scale(0.8);
          }
        }

        @keyframes animeSpawn {
          0% {
            transform: scale(0) rotate(-10deg);
            opacity: 0;
            filter: brightness(2) drop-shadow(0 0 20px rgba(255, 255, 255, 0.8));
          }
          60% {
            transform: scale(1.12) rotate(3deg);
            opacity: 1;
            filter: brightness(1.4) drop-shadow(0 0 12px rgba(200, 200, 200, 0.6));
          }
          80% {
            transform: scale(0.96) rotate(-1deg);
          }
          100% {
            transform: scale(1) rotate(0deg);
            opacity: 1;
            filter: brightness(1) drop-shadow(0 0 0px transparent);
          }
        }

        @keyframes mangaAura {
          0% {
            transform: scale(0.2);
            opacity: 0.9;
          }
          50% {
            transform: scale(1.6);
            opacity: 0.6;
          }
          100% {
            transform: scale(2.2);
            opacity: 0;
          }
        }

        @keyframes mangaBurst {
          0% {
            transform: scale(0) rotate(0deg);
            opacity: 1;
          }
          50% {
            opacity: 1;
          }
          100% {
            transform: scale(1.8) rotate(45deg);
            opacity: 0;
          }
        }

        .animate-spawn {
          animation: animeSpawn 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
          opacity: 0;
        }

        .animate-keycap {
          animation: autoPress 2.5s ease-in-out infinite;
        }

        .animate-cyber-glow {
          animation: cyberGlow 2.5s ease-in-out infinite;
        }

        .manga-aura-ring {
          animation: mangaAura 0.6s cubic-bezier(0.1, 0.8, 0.3, 1) forwards;
        }

        .manga-strike {
          animation: mangaBurst 0.5s ease-out forwards;
        }
      `}</style>

      <div aria-label="Pattern Guard" className="relative flex flex-wrap items-center justify-center gap-2 sm:gap-4 mb-4 select-none pt-6 pb-2 overflow-visible">
        
        {/* Central Manga Impact Star & Monochrome Aura */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-20">
          <div className={`absolute rounded-full border-2 border-white/80 bg-white/10 blur-[2px] manga-aura-ring ${currentSize.aura}`} />
          
          <svg className={`absolute text-white manga-strike ${currentSize.star}`} viewBox="0 0 100 100" fill="currentColor">
            <path d="M50 0 L58 35 L93 25 L68 50 L93 75 L58 65 L50 100 L42 65 L7 75 L32 50 L7 25 L42 35 Z" />
          </svg>
          
          <svg className={`absolute text-zinc-300 manga-strike ${currentSize.starSmall}`} style={{ animationDelay: '0.08s' }} viewBox="0 0 100 100" fill="currentColor">
            <path d="M50 0 L58 35 L93 25 L68 50 L93 75 L58 65 L50 100 L42 65 L7 75 L32 50 L7 25 L42 35 Z" />
          </svg>
        </div>

        {letters.map((item, index) => {
          const distanceFromCenter = Math.abs(index - centerIndex);
          const spawnDelay = 0.15 + distanceFromCenter * 0.07;
          const loopDelay = distanceFromCenter * 0.12;

          return (
            <React.Fragment key={index}>
              {index === 7 && <div className="basis-full h-0" aria-hidden="true" />}
              <div
                className="relative flex items-center justify-center cursor-pointer animate-spawn"
                style={{ animationDelay: `${spawnDelay}s` }}
              >
                <div
                  className="relative flex items-center justify-center animate-keycap"
                  style={{ animationDelay: `${0.8 + loopDelay}s` }}
                >
                {/* Clean Cyber Blue Glowing Aura Layer Behind Keycap */}
                {glowingAura && (
                  <div 
                    className="absolute -inset-2 rounded-[24px] bg-gradient-to-r from-cyan-500 to-blue-600 opacity-0 blur-md pointer-events-none animate-cyber-glow z-0"
                    style={{ animationDelay: `${0.8 + loopDelay}s` }}
                  />
                )}

                <div className="absolute inset-0 rounded-[20px] bg-black/60 blur-[10px] pointer-events-none z-10" />

                <div className={`relative z-20 overflow-hidden bg-[#1a1a1a] rounded-[20px] border-none shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),inset_0_-6px_1px_-4px_rgba(0,0,0,0.9),inset_0_-15px_6px_-8px_rgba(0,0,0,0.8),0_10px_20px_rgba(0,0,0,0.6)] ${currentSize.keycap}`}>
                  <div className={`absolute inset-0 rounded-[16px] border-l-[10px] border-l-[#1f1f1f] border-r-[10px] border-r-[#1f1f1f] border-b-[12px] border-b-[#0d0d0d] filter blur-[2px] pointer-events-none ${currentSize.borderT}`} />

                  <div className={`absolute rounded-[14px] bg-gradient-to-b from-[#181818] to-[#242424] flex items-center justify-center ${currentSize.inset}`}>
                    <span className={`relative z-10 font-black font-mono tracking-tighter text-[#d4d4d4] drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)] ${currentSize.text}`}>
                      {item.char}
                    </span>
                  </div>
                </div>

                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </>
  );
}
