'use client';

import React from 'react';
import { Compass, ArrowRight } from 'lucide-react';

interface SimpleFooterWithFourGridsProps {
  onOpenAuth?: (mode?: 'login' | 'signup') => void;
  onLaunchStudio?: () => void;
  className?: string;
}

export function SimpleFooterWithFourGrids({
  onOpenAuth,
  onLaunchStudio,
  className = "",
}: SimpleFooterWithFourGridsProps) {
  return (
    <footer className={`relative w-full border-t border-white/10 bg-[#030712] pt-16 pb-8 overflow-hidden ${className}`}>
      {/* Top Content Row */}
      <div className="max-w-6xl mx-auto px-6 relative z-10">
        <div className="flex flex-col lg:flex-row justify-between gap-12">
          {/* Left Brand & Copyright */}
          <div className="space-y-4 max-w-sm">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-lg bg-white flex items-center justify-center text-[#030712] shadow-md shadow-white/20">
                <Compass className="h-4 w-4 text-[#030712]" />
              </div>
              <span className="font-extrabold text-lg tracking-tight text-white font-outfit">
                Neurolytix
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              Autonomous Data Science, Dynamic Visual EDA, and Multi-Agent JEV Decision Intelligence Studio.
            </p>
            <p className="text-xs text-slate-500 font-sans pt-2">
              © copyright Neurolytix 2026. All rights reserved.
            </p>
          </div>

          {/* Right 4-Grid Columns (Exact Match to Image 1) */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 text-xs">
            {/* Grid 1: Pages */}
            <div className="space-y-3">
              <h4 className="font-bold text-white font-outfit text-sm">Pages</h4>
              <ul className="space-y-2 text-slate-400">
                <li>
                  <a href="#pipeline" className="hover:text-white transition">All Features</a>
                </li>
                <li>
                  <button onClick={onLaunchStudio} className="hover:text-white transition cursor-pointer text-left">
                    Studio
                  </button>
                </li>
                <li>
                  <a href="#eda" className="hover:text-white transition">Dynamic EDA</a>
                </li>
                <li>
                  <a href="#automl" className="hover:text-white transition">AutoML & Deploy</a>
                </li>
                <li>
                  <a href="#jev" className="hover:text-white transition">JEV Decisions</a>
                </li>
              </ul>
            </div>

            {/* Grid 2: Socials */}
            <div className="space-y-3">
              <h4 className="font-bold text-white font-outfit text-sm">Socials</h4>
              <ul className="space-y-2 text-slate-400">
                <li>
                  <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-white transition">GitHub</a>
                </li>
                <li>
                  <a href="https://twitter.com" target="_blank" rel="noreferrer" className="hover:text-white transition">Twitter / X</a>
                </li>
                <li>
                  <a href="https://discord.com" target="_blank" rel="noreferrer" className="hover:text-white transition">Discord</a>
                </li>
                <li>
                  <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="hover:text-white transition">LinkedIn</a>
                </li>
                <li>
                  <a href="https://huggingface.co" target="_blank" rel="noreferrer" className="hover:text-white transition">HuggingFace</a>
                </li>
              </ul>
            </div>

            {/* Grid 3: Legal */}
            <div className="space-y-3">
              <h4 className="font-bold text-white font-outfit text-sm">Legal</h4>
              <ul className="space-y-2 text-slate-400">
                <li>
                  <a href="#" className="hover:text-white transition">Privacy Policy</a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">Terms of Service</a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">Cookie Policy</a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">Security Audit</a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition">Ethics Statement</a>
                </li>
              </ul>
            </div>

            {/* Grid 4: Register / Access */}
            <div className="space-y-3">
              <h4 className="font-bold text-white font-outfit text-sm">Register</h4>
              <ul className="space-y-2 text-slate-400">
                <li>
                  <button 
                    onClick={() => onOpenAuth ? onOpenAuth('signup') : onLaunchStudio?.()}
                    className="hover:text-white transition cursor-pointer text-left"
                  >
                    Sign Up
                  </button>
                </li>
                <li>
                  <button 
                    onClick={() => onOpenAuth ? onOpenAuth('login') : onLaunchStudio?.()}
                    className="hover:text-white transition cursor-pointer text-left"
                  >
                    Login
                  </button>
                </li>
                <li>
                  <button 
                    onClick={onLaunchStudio}
                    className="hover:text-white transition cursor-pointer text-left text-blue-400 font-semibold flex items-center gap-1"
                  >
                    <span>Instant Demo</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </li>
                <li>
                  <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-white transition">
                    FastAPI Swagger
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Massive Faint Watermark Text (Exact Match to Image 1: "DevStudio" style watermark) */}
      <div className="relative w-full pt-16 pointer-events-none select-none flex items-center justify-center">
        <span className="text-[80px] sm:text-[130px] md:text-[170px] lg:text-[210px] font-black font-outfit text-white/[0.04] tracking-tight leading-none text-center">
          Neurolytix
        </span>
      </div>
    </footer>
  );
}
