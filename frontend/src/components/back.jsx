import React, { useEffect, useRef } from 'react';

const MangaBackground = ({ children }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.parentElement.offsetWidth);
    let height = (canvas.height = canvas.parentElement.offsetHeight);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
    };

    window.addEventListener('resize', handleResize);

    const particleCount = Math.floor((width * height) / 12000);
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 2.5 + 0.5,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: -Math.random() * 1.5 - 0.2,
        opacity: Math.random() * 0.7 + 0.3,
        pulseSpeed: Math.random() * 0.02 + 0.005,
      });
    }

    const render = () => {
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, width, height);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.012)';
      for (let x = 0; x < width; x += 30) {
        ctx.fillRect(x, 0, 1, height);
      }

      particles.forEach((p) => {
        p.x += p.speedX;
        p.y += p.speedY;

        if (p.y < 0) {
          p.y = height + 10;
          p.x = Math.random() * width;
        }
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;

        p.opacity += Math.sin(Date.now() * p.pulseSpeed) * 0.01;
        const currentOpacity = Math.max(0.1, Math.min(1, p.opacity));

        ctx.fillStyle = `rgba(255, 255, 255, ${currentOpacity})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        if (p.size > 2) {
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(p.x, p.y, 0.8, 0.8);
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="relative w-full overflow-hidden bg-black">
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none z-0 w-full h-full" />
      <div className="relative z-10 w-full h-full flex flex-col items-center">
        {children}
      </div>
    </div>
  );
};

export default MangaBackground;