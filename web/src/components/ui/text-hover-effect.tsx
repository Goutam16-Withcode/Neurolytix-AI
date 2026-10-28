'use client';

import React, { useRef, useEffect, useState } from 'react';

interface TextHoverEffectProps {
  text: string;
  duration?: number;
  className?: string;
}

export function TextHoverEffect({ text, className = '' }: TextHoverEffectProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [cursor, setCursor] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState(false);
  const [maskPosition, setMaskPosition] = useState({ cx: '50%', cy: '50%' });

  useEffect(() => {
    if (svgRef.current && cursor.x !== null && cursor.y !== null) {
      const rect = svgRef.current.getBoundingClientRect();
      const cxPercentage = ((cursor.x - rect.left) / rect.width) * 100;
      const cyPercentage = ((cursor.y - rect.top) / rect.height) * 100;
      setMaskPosition({
        cx: `${cxPercentage}%`,
        cy: `${cyPercentage}%`,
      });
    }
  }, [cursor]);

  return (
    <div className={`relative select-none w-full flex items-center justify-center ${className}`}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox="0 0 1000 200"
        xmlns="http://www.w3.org/2000/svg"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onMouseMove={(e) => setCursor({ x: e.clientX, y: e.clientY })}
        className="w-full h-auto cursor-default overflow-visible"
      >
        <defs>
          {/* Glowing Gradient */}
          <linearGradient id="textGradient" gradientUnits="userSpaceOnUse" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#00D2FF" />
            <stop offset="25%" stopColor="#3B82F6" />
            <stop offset="50%" stopColor="#6366F1" />
            <stop offset="75%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#00D2FF" />
          </linearGradient>

          {/* Radial Light Reveal Mask that tracks mouse */}
          <radialGradient
            id="revealMask"
            gradientUnits="userSpaceOnUse"
            r="20%"
            cx={maskPosition.cx}
            cy={maskPosition.cy}
            className="transition-all duration-75 ease-out"
          >
            <stop offset="0%" stopColor="white" />
            <stop offset="100%" stopColor="black" />
          </radialGradient>

          <mask id="textMask">
            <rect
              x="0"
              y="0"
              width="100%"
              height="100%"
              fill="url(#revealMask)"
            />
          </mask>
        </defs>

        {/* Base Faint Outline */}
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          strokeWidth="0.8"
          className="font-black font-outfit fill-transparent stroke-white/15 tracking-widest text-[110px]"
          style={{ letterSpacing: '0.12em' }}
        >
          {text}
        </text>

        {/* Revealed Glowing Text on Hover */}
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          stroke="url(#textGradient)"
          strokeWidth="1.2"
          mask="url(#textMask)"
          className={`font-black font-outfit fill-transparent tracking-widest text-[110px] transition-opacity duration-300 ${
            hovered ? 'opacity-100' : 'opacity-0'
          }`}
          style={{ letterSpacing: '0.12em' }}
        >
          {text}
        </text>

        {/* Subtle filled gradient text on hover */}
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="url(#textGradient)"
          mask="url(#textMask)"
          className={`font-black font-outfit tracking-widest text-[110px] transition-opacity duration-300 ${
            hovered ? 'opacity-70' : 'opacity-0'
          }`}
          style={{ letterSpacing: '0.12em' }}
        >
          {text}
        </text>
      </svg>
    </div>
  );
}
