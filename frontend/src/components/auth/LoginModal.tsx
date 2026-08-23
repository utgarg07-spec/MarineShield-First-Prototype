import React, { useState } from 'react';
import { X, Shield, KeyRound, Mail, User, BadgeCheck, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { useApp } from '../../context/AppContext';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  onSwitchToRegister: () => void;
  onDemoMode: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  onSwitchToRegister,
  onDemoMode,
}) => {
  const { loginWithEmailOrId, loginWithGoogle, sendPasswordReset, hasFirebaseConfig } = useApp();
  
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [isForgot, setIsForgot] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    if (!identifier.trim()) {
      setErrorMessage('Username / Operator ID / Email is required');
      return;
    }
    if (!password) {
      setErrorMessage('Password is required');
      return;
    }

    setLoading(true);
    try {
      if (hasFirebaseConfig) {
        await loginWithEmailOrId(identifier.trim(), password);
      }
      onSuccess();
    } catch (error: any) {
      setErrorMessage(error.message || 'ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !identifier.includes('@')) {
      setErrorMessage('Valid Email address is required for password reset');
      return;
    }
    setErrorMessage(null);
    try {
      if (hasFirebaseConfig) {
        await sendPasswordReset(identifier.trim());
      }
      setInfoMessage(`Password reset instructions sent to ${identifier.trim()}`);
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to send password reset email');
    }
  };

  const handleGoogle = async () => {
    setErrorMessage(null);
    try {
      if (hasFirebaseConfig) {
        await loginWithGoogle();
        onSuccess();
      } else {
        setErrorMessage('Firebase SDK environment is missing configuration. Please use Demo Mode.');
      }
    } catch (error: any) {
      setErrorMessage(error.message || 'ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden p-6 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider">
              {isForgot ? 'Reset Password' : 'Operator Authentication'}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMessage && (
          <div className="p-3.5 rounded bg-red-950/60 border border-red-800/80 text-xs text-red-200 space-y-2">
            <div className="flex items-start gap-2 font-semibold">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
            {errorMessage.includes('ACCOUNT DOES NOT EXIST') && (
              <div className="pt-2 border-t border-red-900/60 flex items-center justify-between">
                <span className="text-[11px] text-slate-300">New operator?</span>
                <button
                  type="button"
                  onClick={onSwitchToRegister}
                  className="px-2.5 py-1 rounded bg-red-900/80 hover:bg-red-800 text-white font-bold text-xs transition-colors cursor-pointer"
                >
                  Create Account Now
                </button>
              </div>
            )}
          </div>
        )}

        {infoMessage && (
          <div className="p-3 rounded bg-emerald-950/40 border border-emerald-800/60 text-xs text-emerald-300 flex items-start gap-2">
            <BadgeCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{infoMessage}</span>
          </div>
        )}

        {!isForgot ? (
          <form onSubmit={handleLoginSubmit} className="space-y-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Username / Operator ID / Email
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="e.g. OP-8492 or operator@marineshield.gov"
                  className="w-full bg-slate-950 border border-slate-800 rounded pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Password</label>
                <button
                  type="button"
                  onClick={() => setIsForgot(true)}
                  className="text-[10px] text-cyan-400 hover:underline cursor-pointer"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950 border border-slate-800 rounded pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <Button type="submit" className="w-full mt-2" disabled={loading}>
              {loading ? 'Verifying Registry...' : 'Login'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleForgotSubmit} className="space-y-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Registered Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="email"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="operator@marineshield.gov"
                  className="w-full bg-slate-950 border border-slate-800 rounded pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <Button type="submit" className="w-full">Send Reset Email</Button>

            <button
              type="button"
              onClick={() => setIsForgot(false)}
              className="text-xs text-slate-400 hover:text-slate-200 text-center block w-full pt-1"
            >
              Back to Login
            </button>
          </form>
        )}

        <div className="space-y-3 pt-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={handleGoogle}
            className="w-full py-2 px-3 rounded bg-slate-950 hover:bg-slate-800/80 border border-slate-800 text-xs font-semibold text-slate-300 transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.8 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z" />
              <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z" />
              <path fill="#FBBC05" d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12.4 0 15.3c0 2.9.7 5.6 1.9 8l3.7-2.9c-.2-.7-.4-1.5-.4-2.3z" />
              <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16c1.8 3.7 5.6 7 10.1 7z" />
            </svg>
            <span>Login with Google</span>
          </button>

          <div className="flex items-center justify-between text-xs pt-1">
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="text-cyan-400 hover:underline cursor-pointer"
            >
              New user? Create Account
            </button>

            <button
              type="button"
              onClick={onDemoMode}
              className="text-xs font-bold text-amber-400 hover:text-amber-300 transition-colors cursor-pointer"
            >
              Continue in Demo Mode
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
