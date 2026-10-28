'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/auth-context';
import { 
  X, 
  Lock, 
  Mail, 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  Brain,
  RotateCw
} from 'lucide-react';

interface AuthModalProps {
  onSuccess?: () => void;
}

export function AuthModal({ onSuccess }: AuthModalProps) {
  const { 
    isAuthModalOpen, 
    closeAuthModal, 
    authMode, 
    setAuthMode, 
    login, 
    signup, 
    loginWithGoogle, 
    loginAsGuest 
  } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isAuthModalOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }
    setSubmitting(true);
    setErrorMsg(null);

    try {
      if (authMode === 'login') {
        await login(email, password);
      } else {
        await signup(email, password);
      }
      onSuccess?.();
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication error.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
      onSuccess?.();
    } catch (e: any) {
      setErrorMsg(e.message || 'Google login error');
    }
  };

  const handleGuestLogin = () => {
    loginAsGuest();
    onSuccess?.();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4">
      {/* Blurred Backdrop */}
      <div 
        onClick={closeAuthModal} 
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity" 
      />

      {/* Royal Sapphire Glass Card */}
      <div className="relative w-full max-w-md rounded-2xl bg-[#090D18] border border-blue-500/20 shadow-2xl p-7 text-white z-10 overflow-hidden">
        {/* Diffuse Sapphire Ambient Glow */}
        <div className="absolute -top-24 -right-24 w-56 h-56 bg-blue-600/30 blur-3xl pointer-events-none rounded-full" />
        <div className="absolute -bottom-24 -left-24 w-56 h-56 bg-indigo-600/20 blur-3xl pointer-events-none rounded-full" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10 relative z-10">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/30">
              <Brain className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white font-outfit">
                {authMode === 'login' ? 'Sign in to Neurolytix Studio' : 'Create Free Account'}
              </h3>
              <p className="text-[11px] text-slate-400">Firebase Authentication</p>
            </div>
          </div>
          <button
            onClick={closeAuthModal}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4 relative z-10">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          {errorMsg && (
            <p className="text-xs text-rose-400 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
              {errorMsg}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {submitting ? (
              <RotateCw className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <span>{authMode === 'login' ? 'Sign In & Open Studio' : 'Create Account & Enter'}</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="my-4 flex items-center gap-3 relative z-10">
          <div className="h-px bg-white/10 flex-1" />
          <span className="text-[10px] text-slate-500 uppercase font-semibold">Or continue with</span>
          <div className="h-px bg-white/10 flex-1" />
        </div>

        {/* Social / Guest Options */}
        <div className="space-y-2 relative z-10">
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full py-2 px-3 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold text-slate-200 transition flex items-center justify-center gap-2 cursor-pointer"
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.9c2.28-2.1 3.645-5.2 3.645-9.15z"/>
              <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.9-3.05c-1.08.72-2.45 1.16-4.03 1.16-3.1 0-5.74-2.1-6.68-4.93H1.21v3.15C3.25 21.43 7.32 24 12 24z"/>
              <path fill="#FBBC05" d="M5.32 14.27c-.24-.73-.38-1.5-.38-2.27s.14-1.54.38-2.27V6.58H1.21C.44 8.11 0 9.99 0 12s.44 3.89 1.21 5.42l4.11-3.15z"/>
              <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.32 0 3.25 2.57 1.21 6.58l4.11 3.15c.94-2.83 3.58-4.98 6.68-4.98z"/>
            </svg>
            <span>Google Account</span>
          </button>

          <button
            type="button"
            onClick={handleGuestLogin}
            className="w-full py-2.5 px-3 rounded-full bg-gradient-to-r from-blue-600/30 to-indigo-600/30 hover:from-blue-600/40 hover:to-indigo-600/40 border border-blue-500/40 text-xs font-bold text-white transition flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-blue-600/20"
          >
            <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            <span>Instant Demo Guest Access (Direct To Dashboard)</span>
          </button>
        </div>

        {/* Footer Toggle */}
        <div className="mt-4 pt-3 border-t border-white/10 text-center text-xs text-slate-400 relative z-10">
          {authMode === 'login' ? (
            <p>
              Don&apos;t have an account?{' '}
              <button
                type="button"
                onClick={() => setAuthMode('signup')}
                className="font-bold text-blue-400 hover:text-blue-300 underline cursor-pointer"
              >
                Sign up free
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setAuthMode('login')}
                className="font-bold text-blue-400 hover:text-blue-300 underline cursor-pointer"
              >
                Log in
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
