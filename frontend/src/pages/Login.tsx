import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'http://127.0.0.1:8000';

export default function Login() {
  const navigate  = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const r = await axios.post(`${API}/api/auth/login`, { username, password });
      localStorage.setItem('token', r.data.data?.token || 'demo-token');
      localStorage.setItem('user', r.data.data?.user || username);
      navigate('/app');
    } catch {
      setError('Invalid credentials. Try any username/password or use Demo Mode.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = () => {
    localStorage.setItem('demo_mode', 'true');
    localStorage.setItem('token', 'demo-token');
    navigate('/app');
  };

  const inp = {
    width: '100%', padding: '12px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)',
    background: 'rgba(255,255,255,0.06)', color: '#fff', fontSize: 14, outline: 'none',
  } as React.CSSProperties;

  return (
    <div style={{ minHeight: '100vh', background: '#060B18', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui,sans-serif', color: '#fff' }}>
      <div style={{ width: 380, padding: 36, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 20, boxShadow: '0 20px 60px rgba(0,0,0,0.4)' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ width: 52, height: 52, background: 'linear-gradient(135deg,#2563EB,#06B6D4)', borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 26, margin: '0 auto 12px' }}>
            AI
          </div>
          <div style={{ fontSize: 22, fontWeight: 600, background: 'linear-gradient(90deg,#60A5FA,#06B6D4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            JobPilot AI
          </div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>Your personal career agent</div>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>Username</div>
            <input style={inp} type="text" value={username} onChange={e => setUsername(e.target.value)}
              placeholder="Enter username" autoComplete="username" />
          </div>
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 6 }}>Password</div>
            <input style={inp} type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="Enter password" autoComplete="current-password" />
          </div>

          {error && (
            <div style={{ padding: '10px 12px', borderRadius: 8, background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.25)', color: '#FB7185', fontSize: 12, marginBottom: 14 }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={loading}
            style={{ width: '100%', padding: '13px', background: 'linear-gradient(135deg,#2563EB,#06B6D4)', border: 'none', borderRadius: 12, color: '#fff', fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', marginBottom: 10, opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <button onClick={handleDemo}
          style={{ width: '100%', padding: '13px', background: 'transparent', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12, color: 'rgba(255,255,255,0.55)', fontSize: 14, cursor: 'pointer' }}>
          Skip - Demo Mode
        </button>

        <div style={{ textAlign: 'center', marginTop: 16, fontSize: 11, color: 'rgba(255,255,255,0.2)' }}>
          In demo mode, any credentials work
        </div>
      </div>
    </div>
  );
}
