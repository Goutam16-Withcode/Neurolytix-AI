import React from 'react';

interface AuroraBackgroundProps {
  children?: React.ReactNode;
  className?: string;
}

export function AuroraBackground({ children, className = '' }: AuroraBackgroundProps) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      {/* Ambient Aurora Glow Gradients */}
      <div className="pointer-events-none absolute -top-40 -left-40 h-[500px] w-[500px] rounded-full bg-gradient-to-tr from-indigo-200/40 via-purple-100/30 to-pink-200/20 blur-3xl opacity-70 animate-aurora" />
      <div className="pointer-events-none absolute top-10 right-0 h-[450px] w-[450px] rounded-full bg-gradient-to-br from-cyan-200/35 via-blue-100/30 to-emerald-100/20 blur-3xl opacity-60 animate-aurora" />
      <div className="pointer-events-none absolute -bottom-32 left-1/3 h-[400px] w-[600px] rounded-full bg-gradient-to-r from-violet-100/40 to-indigo-100/30 blur-3xl opacity-50" />
      
      {/* Geometric Aceternity Light Grid */}
      <div className="pointer-events-none absolute inset-0 aceternity-grid opacity-60" />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
