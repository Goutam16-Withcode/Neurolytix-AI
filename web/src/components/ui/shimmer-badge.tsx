import React from 'react';

interface ShimmerBadgeProps {
  children: React.ReactNode;
  variant?: 'indigo' | 'emerald' | 'amber' | 'cyan' | 'purple';
  className?: string;
}

export function ShimmerBadge({ children, variant = 'indigo', className = '' }: ShimmerBadgeProps) {
  const variantStyles = {
    indigo: 'bg-indigo-50/80 text-indigo-700 border-indigo-200/80 shadow-indigo-100/50',
    emerald: 'bg-emerald-50/80 text-emerald-700 border-emerald-200/80 shadow-emerald-100/50',
    amber: 'bg-amber-50/80 text-amber-700 border-amber-200/80 shadow-amber-100/50',
    cyan: 'bg-cyan-50/80 text-cyan-700 border-cyan-200/80 shadow-cyan-100/50',
    purple: 'bg-purple-50/80 text-purple-700 border-purple-200/80 shadow-purple-100/50',
  };

  return (
    <div
      className={`relative inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full border shadow-sm backdrop-blur-sm overflow-hidden ${variantStyles[variant]} ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/50 to-transparent -translate-x-full animate-[shimmer_3s_infinite]" />
      {children}
    </div>
  );
}
