import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, KeyRound, Mail } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Button } from '../components/ui/Button';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginWithEmailOrId, loginDemo, hasFirebaseConfig } = useApp();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) {
      setError('Email and password are required.');
      return;
    }
    setLoading(true);
    try {
      if (hasFirebaseConfig) {
        await loginWithEmailOrId(email, password);
      } else {
        loginDemo();
      }
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoMode = () => {
    loginDemo();
    navigate('/dashboard');
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-slate-950 overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-cyan-900/10 rounded-full blur-3xl" />

      <div className="relative z-10 w-full max-w-md px-6">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 backdrop-blur-md shadow-2xl space-y-6">
          <div className="flex flex-col items-center text-center space-y-2">
            <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700/60 flex items-center justify-center mb-1">
              <Shield className="w-6 h-6 text-cyan-400" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-wide">
              MARINESHIELD <span className="text-cyan-400">LOGIN</span>
            </h2>
            <p className="text-xs text-slate-400">
              Firebase Operator Authentication
            </p>
          </div>

          {error && (
            <div className="p-3 rounded bg-red-950/40 border border-red-800/60 text-xs text-red-300">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500/70"
                  placeholder="operator@marineshield.gov"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                Password
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500/70"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Authenticating...' : 'Login'}
            </Button>
          </form>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
            <button
              type="button"
              onClick={handleDemoMode}
              className="text-amber-400 hover:text-amber-300 font-bold cursor-pointer"
            >
              Continue in Demo Mode
            </button>

            <button
              type="button"
              onClick={() => navigate('/')}
              className="text-slate-400 hover:text-slate-200 cursor-pointer"
            >
              Back to Landing
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
