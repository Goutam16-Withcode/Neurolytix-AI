'use client';

import React, { useState } from 'react';
import { 
  Compass, 
  Sparkles, 
  User, 
  ArrowRight, 
  BarChart3, 
  Cpu, 
  Scale, 
  Layers, 
  Database, 
  ChevronDown,
  Menu,
  X,
  FileText
} from 'lucide-react';

export interface NavDropdownItem {
  title: string;
  description: string;
  icon: any;
  tag?: string;
  action?: () => void;
  link?: string;
}

export interface NavMenuItem {
  name: string;
  link: string;
  dropdown?: NavDropdownItem[];
}

interface NavbarDarkShadowProps {
  navItems?: NavMenuItem[];
  user: any;
  onLaunchStudio: () => void;
  onOpenAuth: (mode?: 'login' | 'signup') => void;
  onLogout: () => void;
  className?: string;
}

export function NavbarDarkShadow({
  navItems,
  user,
  onLaunchStudio,
  onOpenAuth,
  onLogout,
  className = '',
}: NavbarDarkShadowProps) {
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const defaultNavItems: NavMenuItem[] = navItems || [
    {
      name: 'Capabilities',
      link: '#pipeline',
      dropdown: [
        {
          title: 'Dynamic Visual EDA',
          description: 'Automated histograms, correlation matrices & NLP keywords inferred by data type.',
          icon: BarChart3,
          tag: 'Real-time',
          link: '#eda',
        },
        {
          title: 'Multi-Model AutoML & Deploy',
          description: 'CatBoost, LightGBM, XGBoost, Prophet & NLP with live inference simulator.',
          icon: Cpu,
          tag: 'Sub-10ms',
          link: '#automl',
        },
        {
          title: 'Agentic RAG & JEV Engine',
          description: 'Multi-agent deliberation: Proposers ➔ Verifier Shield ➔ JEV Verdict.',
          icon: Scale,
          tag: 'JEV v2',
          link: '#jev',
        },
        {
          title: 'Executive Dossier Reports',
          description: 'Auto-compiled executive briefings with print & PDF export readiness.',
          icon: FileText,
          tag: 'Export',
          link: '#reports',
        },
      ],
    },
    {
      name: 'Dynamic EDA',
      link: '#eda',
    },
    {
      name: 'AutoML & Deploy',
      link: '#automl',
    },
    {
      name: 'JEV Decisions',
      link: '#jev',
    },
    {
      name: 'Enterprise',
      link: '#pricing',
    },
  ];

  return (
    <header className={`fixed top-4 inset-x-0 z-50 max-w-6xl mx-auto px-4 ${className}`}>
      {/* Outer Floating Pill with Aceternity Dark Shadow & Glowing Border */}
      <div 
        className="relative rounded-full border border-white/[0.12] bg-[#080C17]/85 backdrop-blur-2xl px-4 py-2 sm:px-6 sm:py-2.5 flex items-center justify-between shadow-[0_20px_50px_rgba(0,0,0,0.95),0_0_30px_rgba(37,99,235,0.18),inset_0_1px_1px_rgba(255,255,255,0.15)] transition-all duration-300"
        onMouseLeave={() => setActiveMenu(null)}
      >
        {/* Top subtle highlight beam */}
        <div className="absolute top-0 inset-x-12 h-[1px] bg-gradient-to-r from-transparent via-blue-400/60 to-transparent pointer-events-none" />

        {/* Brand Logo & Name */}
        <a 
          href="#"
          className="flex items-center gap-2.5 group cursor-pointer"
        >
          <div className="relative h-7 w-7 sm:h-8 sm:w-8 rounded-full bg-white flex items-center justify-center text-[#030712] shadow-md shadow-white/30 group-hover:scale-105 transition duration-200">
            <Compass className="h-4 w-4 sm:h-4.5 sm:w-4.5 text-[#030712]" />
            <span className="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full bg-emerald-400 ring-2 ring-[#080C17] animate-pulse" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-sm sm:text-base tracking-tight text-white font-outfit">
                Neurolytix
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 hidden md:inline">
                AI Studio
              </span>
            </div>
          </div>
        </a>

        {/* Center Desktop Navigation with Aceternity Dropdowns */}
        <nav className="hidden lg:flex items-center gap-1 text-xs font-semibold text-slate-300">
          {defaultNavItems.map((item) => {
            const hasDropdown = Boolean(item.dropdown && item.dropdown.length > 0);
            const isItemActive = activeMenu === item.name;

            return (
              <div
                key={item.name}
                className="relative"
                onMouseEnter={() => hasDropdown && setActiveMenu(item.name)}
              >
                <a
                  href={item.link}
                  className={`flex items-center gap-1 px-3.5 py-1.5 rounded-full transition-all duration-200 cursor-pointer ${
                    isItemActive
                      ? 'text-white bg-white/10 shadow-inner'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span>{item.name}</span>
                  {hasDropdown && (
                    <ChevronDown className={`h-3 w-3 text-slate-400 transition-transform duration-200 ${
                      isItemActive ? 'rotate-180 text-white' : ''
                    }`} />
                  )}
                </a>

                {/* Dropdown Menu Card with Aceternity Dark Shadow styling */}
                {hasDropdown && isItemActive && (
                  <div 
                    className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-96 rounded-2xl bg-[#090D1A]/95 border border-white/15 p-3 shadow-[0_25px_60px_rgba(0,0,0,0.95),0_0_40px_rgba(37,99,235,0.25)] backdrop-blur-2xl animate-in fade-in zoom-in-95 duration-150"
                  >
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-3 py-1 font-semibold border-b border-white/10 mb-2 flex items-center justify-between">
                      <span>Autonomous Platform Suite</span>
                      <span className="text-blue-400">v2.0 Active</span>
                    </div>

                    <div className="space-y-1">
                      {item.dropdown!.map((sub, sIdx) => {
                        const Icon = sub.icon;
                        return (
                          <a
                            key={sIdx}
                            href={sub.link || '#'}
                            className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-white/10 transition-colors group cursor-pointer"
                          >
                            <div className="h-8 w-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-600 group-hover:text-white transition">
                              <Icon className="h-4 w-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-bold text-white group-hover:text-blue-300 transition">
                                  {sub.title}
                                </span>
                                {sub.tag && (
                                  <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40 font-mono">
                                    {sub.tag}
                                  </span>
                                )}
                              </div>
                              <p className="text-[11px] text-slate-400 leading-snug line-clamp-2 mt-0.5">
                                {sub.description}
                              </p>
                            </div>
                          </a>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Right Action / Auth CTA */}
        <div className="flex items-center gap-2 sm:gap-3">
          {user ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-slate-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="max-w-[120px] truncate font-mono text-[11px]">
                  {user.displayName || user.email?.split('@')[0] || 'User'}
                </span>
              </div>
              <button
                onClick={onLaunchStudio}
                className="px-4 py-1.5 sm:px-5 sm:py-2 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-[0_0_20px_rgba(37,99,235,0.5)] transition hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-1.5"
              >
                <span>Enter Studio</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={onLogout}
                className="text-[11px] text-slate-400 hover:text-white underline cursor-pointer px-1 hidden sm:inline"
              >
                Exit
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => onOpenAuth('login')}
                className="hidden sm:inline-block px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-300 hover:text-white transition hover:bg-white/5 cursor-pointer"
              >
                Sign In
              </button>
              <button
                onClick={onLaunchStudio}
                className="px-4 py-1.5 sm:px-5 sm:py-2 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-[0_0_25px_rgba(37,99,235,0.5)] transition hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-1.5"
              >
                <span>Start free</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          )}

          {/* Mobile Menu Hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-1.5 rounded-full bg-white/5 hover:bg-white/10 text-slate-300 transition cursor-pointer"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden mt-2 rounded-2xl bg-[#080C17]/95 border border-white/15 p-4 shadow-[0_20px_50px_rgba(0,0,0,0.95)] backdrop-blur-2xl animate-in fade-in slide-in-from-top-3">
          <nav className="flex flex-col gap-2">
            <a 
              href="#pipeline" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-white/10 hover:text-white flex items-center justify-between"
            >
              <span>Platform Pipeline</span>
              <BarChart3 className="h-4 w-4 text-blue-400" />
            </a>
            <a 
              href="#eda" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-white/10 hover:text-white flex items-center justify-between"
            >
              <span>Dynamic EDA</span>
              <Database className="h-4 w-4 text-blue-400" />
            </a>
            <a 
              href="#automl" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-white/10 hover:text-white flex items-center justify-between"
            >
              <span>AutoML & Deployment</span>
              <Cpu className="h-4 w-4 text-blue-400" />
            </a>
            <a 
              href="#jev" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:bg-white/10 hover:text-white flex items-center justify-between"
            >
              <span>JEV Decision Engine</span>
              <Scale className="h-4 w-4 text-blue-400" />
            </a>

            <div className="pt-2 border-t border-white/10 flex flex-col gap-2">
              {user ? (
                <>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      onLaunchStudio();
                    }}
                    className="w-full py-2.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/40 text-center"
                  >
                    Enter Studio
                  </button>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      onLogout();
                    }}
                    className="w-full py-2 rounded-full bg-white/5 text-slate-300 hover:text-white text-xs text-center"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      onOpenAuth('login');
                    }}
                    className="w-full py-2 rounded-full bg-white/10 text-white text-xs font-semibold"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      onLaunchStudio();
                    }}
                    className="w-full py-2.5 rounded-full bg-blue-600 text-white font-bold text-xs shadow-lg shadow-blue-600/40"
                  >
                    Get Started Free (Open Studio)
                  </button>
                </>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
