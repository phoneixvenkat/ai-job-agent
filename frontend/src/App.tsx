import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import JobHunt from './pages/JobHunt';
import Review from './pages/Review';
import Applications from './pages/Applications';
import Analytics from './pages/Analytics';
import SkillRoadmap from './pages/SkillRoadmap';
import Settings from './pages/Settings';

const navItems = [
  { to: '/',             icon: '⚡', label: 'Dashboard'    },
  { to: '/jobs',         icon: '🔍', label: 'Job Hunt'     },
  { to: '/review',       icon: '📄', label: 'Review'       },
  { to: '/applications', icon: '📋', label: 'Applications' },
  { to: '/analytics',    icon: '📊', label: 'Analytics'    },
  { to: '/skills',       icon: '📚', label: 'Skill Roadmap'},
  { to: '/settings',     icon: '⚙️', label: 'Settings'    },
];

const agentStatus = [
  { name: 'Scout',   color: '#2563EB', active: true  },
  { name: 'Analyst', color: '#06B6D4', active: true  },
  { name: 'Writer',  color: '#10B981', active: true  },
  { name: 'Applier', color: '#6B7280', active: false },
  { name: 'Tracker', color: '#2563EB', active: true  },
];

export default function App() {
  const [time, setTime] = React.useState(new Date());
  React.useEffect(() => { const t = setInterval(() => setTime(new Date()), 1000); return () => clearInterval(t); }, []);

  return (
    <Router>
      <div style={{ display: 'flex', height: '100vh', background: '#060B18', position: 'relative', overflow: 'hidden' }}>

        {/* Animated background */}
        <canvas id="bgCanvas" style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }} />

        {/* Sidebar */}
        <aside style={{ width: 220, background: 'rgba(255,255,255,0.03)', borderRight: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 10, backdropFilter: 'blur(20px)', flexShrink: 0 }}>

          {/* Logo */}
          <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ width: 38, height: 38, background: 'linear-gradient(135deg,#2563EB,#06B6D4)', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, marginBottom: 10, animation: 'float 3s ease-in-out infinite' }}>🤖</div>
            <div style={{ fontSize: 15, fontWeight: 600, background: 'linear-gradient(90deg,#60A5FA,#06B6D4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>JobPilot AI</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)', marginTop: 2 }}>Personal career agent</div>
          </div>

          {/* Nav */}
          <nav style={{ padding: '16px 10px', flex: 1 }}>
            {navItems.map(({ to, icon, label }) => (
              <NavLink key={to} to={to} end={to === '/'}
                style={({ isActive }) => ({
                  display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
                  borderRadius: 10, textDecoration: 'none', fontSize: 13, marginBottom: 3,
                  transition: 'all 0.2s', cursor: 'pointer',
                  background: isActive ? 'linear-gradient(135deg,rgba(37,99,235,0.25),rgba(6,182,212,0.1))' : 'transparent',
                  color: isActive ? '#60A5FA' : 'rgba(255,255,255,0.45)',
                  border: isActive ? '1px solid rgba(37,99,235,0.3)' : '1px solid transparent',
                })}>
                <span style={{ fontSize: 15 }}>{icon}</span>{label}
              </NavLink>
            ))}
          </nav>

          {/* Agent Status */}
          <div style={{ padding: '12px 14px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Agent Status</div>
            {agentStatus.map(a => (
              <div key={a.name} style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6 }}>
                <div style={{ width: 7, height: 7, borderRadius: '50%', background: a.color, boxShadow: a.active ? `0 0 6px ${a.color}` : 'none', animation: a.active ? 'pulse 1.5s ease-in-out infinite' : 'none' }} />
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', flex: 1 }}>{a.name}</span>
                <span style={{ fontSize: 9, padding: '1px 6px', borderRadius: 10, background: a.active ? 'rgba(16,185,129,0.15)' : 'rgba(255,255,255,0.05)', color: a.active ? '#10B981' : 'rgba(255,255,255,0.3)', border: `1px solid ${a.active ? 'rgba(16,185,129,0.3)' : 'transparent'}` }}>
                  {a.active ? 'Active' : 'Idle'}
                </span>
              </div>
            ))}
          </div>

          {/* Clock */}
          <div style={{ padding: '10px 14px', borderTop: '1px solid rgba(255,255,255,0.06)', fontSize: 11, color: 'rgba(255,255,255,0.3)' }}>
            {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} · {time.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </div>
        </aside>

        {/* Main */}
        <main style={{ flex: 1, overflowY: 'auto', position: 'relative', zIndex: 10 }}>
          <Routes>
            <Route path="/"             element={<Dashboard />} />
            <Route path="/jobs"         element={<JobHunt />} />
            <Route path="/review"       element={<Review />} />
            <Route path="/applications" element={<Applications />} />
            <Route path="/analytics"    element={<Analytics />} />
            <Route path="/skills"       element={<SkillRoadmap />} />
            <Route path="/settings"     element={<Settings />} />
          </Routes>
        </main>
      </div>

      <style>{`
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
        @keyframes countUp { from{opacity:0} to{opacity:1} }
      `}</style>

      <ParticleBackground />
    </Router>
  );
}

function ParticleBackground() {
  React.useEffect(() => {
    const canvas = document.getElementById('bgCanvas') as HTMLCanvasElement;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let particles: any[] = [];
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener('resize', resize);
    for (let i = 0; i < 60; i++) {
      particles.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3, r: Math.random() * 1.5 + 0.5, o: Math.random() * 0.4 + 0.1 });
    }
    let raf: number;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(96,165,250,${p.o})`; ctx.fill();
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[j].x - p.x, dy = particles[j].y - p.y, d = Math.sqrt(dx * dx + dy * dy);
          if (d < 100) { ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(particles[j].x, particles[j].y); ctx.strokeStyle = `rgba(96,165,250,${0.06 * (1 - d / 100)})`; ctx.stroke(); }
        }
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize); };
  }, []);
  return null;
}