import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const jobMatches = [
  {
    initial: 'G', role: 'ML Engineer', company: 'Google', salary: '$160k–$220k',
    score: 92, gradient: 'from-blue-500 to-purple-600',
    scoreColor: 'text-emerald-400', barColor: 'from-emerald-400 to-cyan-400',
  },
  {
    initial: 'M', role: 'Data Scientist', company: 'Meta', salary: '$145k–$195k',
    score: 85, gradient: 'from-purple-500 to-pink-600',
    scoreColor: 'text-blue-400', barColor: 'from-blue-400 to-purple-400',
  },
  {
    initial: 'O', role: 'AI Researcher', company: 'OpenAI', salary: '$180k–$250k',
    score: 78, gradient: 'from-cyan-500 to-blue-600',
    scoreColor: 'text-cyan-400', barColor: 'from-cyan-400 to-blue-400',
  },
];

const agentDots = [
  { name: 'Scout',   cls: 'bg-emerald-400',              glow: '' },
  { name: 'Analyst', cls: 'bg-emerald-400',              glow: '' },
  { name: 'Writer',  cls: 'bg-blue-400 animate-pulse',   glow: 'shadow-blue-400' },
  { name: 'Tracker', cls: 'bg-emerald-400',              glow: '' },
  { name: 'Email',   cls: 'bg-emerald-400',              glow: '' },
  { name: 'Applier', cls: 'bg-white/20',                 glow: '' },
];

const MockDashboard: React.FC = () => (
  <motion.div
    animate={{ y: [0, -12, 0] }}
    transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
    className="relative"
  >
    {/* Glow halo */}
    <div className="absolute -inset-4 bg-gradient-to-br from-indigo-500/20 via-purple-500/15 to-emerald-500/10 rounded-3xl blur-2xl -z-10" />
    <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-3xl blur-md -z-10" />

    {/* Card shell */}
    <div
      className="relative rounded-2xl overflow-hidden shadow-2xl"
      style={{
        background: 'rgba(10,10,30,0.85)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99,102,241,0.2)',
      }}
    >
      {/* Top gradient bar */}
      <div className="h-[1px] bg-gradient-to-r from-indigo-500/0 via-indigo-400/60 to-indigo-500/0" />

      <div className="p-5 space-y-4">
        {/* Window chrome */}
        <div className="flex items-center justify-between">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          <span className="text-white/25 text-[11px] font-mono tracking-wide">JobPilot AI — Live</span>
          <div className="flex items-center gap-1.5 text-emerald-400 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
            <span className="font-medium">Active</span>
          </div>
        </div>

        {/* KPI row */}
        <div className="grid grid-cols-3 gap-2.5">
          {[
            { n: '258', l: 'Jobs Found', g: 'from-indigo-400 to-purple-400', glow: 'rgba(99,102,241,0.15)' },
            { n: '42',  l: 'Applied',    g: 'from-emerald-400 to-cyan-400',  glow: 'rgba(52,211,153,0.15)' },
            { n: '8',   l: 'Interviews', g: 'from-pink-400 to-purple-400',   glow: 'rgba(244,114,182,0.15)' },
          ].map(({ n, l, g, glow }) => (
            <div
              key={l}
              className="rounded-xl p-3 text-center"
              style={{ background: `radial-gradient(circle at 50% 0%, ${glow}, rgba(255,255,255,0.03) 70%)`, border: '1px solid rgba(255,255,255,0.06)' }}
            >
              <div className={`text-[22px] font-black bg-gradient-to-r ${g} bg-clip-text text-transparent leading-none`}>{n}</div>
              <div className="text-white/35 text-[10px] mt-1 font-medium">{l}</div>
            </div>
          ))}
        </div>

        {/* Label */}
        <div className="flex items-center gap-2">
          <div className="text-white/25 text-[9px] uppercase tracking-[0.12em] font-semibold">Top Matches Today</div>
          <div className="flex-1 h-px bg-white/[0.06]" />
          <span className="text-emerald-400/60 text-[9px] font-mono">AI Scored</span>
        </div>

        {/* Job match rows */}
        {jobMatches.map(({ initial, role, company, salary, score, gradient, scoreColor, barColor }) => (
          <div
            key={company}
            className="rounded-xl p-3 flex items-center gap-3"
            style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.05)' }}
          >
            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-lg`}>
              {initial}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-white text-xs font-semibold truncate">{role} — {company}</div>
              <div className="text-white/30 text-[10px] mt-0.5">{salary} · Remote</div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <div className="w-14 h-1.5 bg-white/[0.08] rounded-full overflow-hidden">
                <div className={`h-full bg-gradient-to-r ${barColor} rounded-full`} style={{ width: `${score}%` }} />
              </div>
              <span className={`${scoreColor} text-[11px] font-bold w-7 text-right`}>{score}%</span>
            </div>
          </div>
        ))}

        {/* Agent status strip */}
        <div className="rounded-xl p-3" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-white/25 text-[9px] uppercase tracking-[0.12em] font-semibold">Agent Status</span>
            <span className="text-white/20 text-[9px] font-mono">6 running</span>
          </div>
          <div className="grid grid-cols-3 gap-x-3 gap-y-1.5">
            {agentDots.map(({ name, cls }) => (
              <div key={name} className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cls}`} />
                <span className="text-white/45 text-[10px]">{name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Activity bar (fake mini chart) */}
        <div className="flex items-end gap-1 h-8 px-1">
          {[40, 65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88].map((h, i) => (
            <motion.div
              key={i}
              className="flex-1 rounded-sm bg-gradient-to-t from-indigo-500/60 to-purple-500/30"
              initial={{ height: 0 }}
              animate={{ height: `${h}%` }}
              transition={{ duration: 0.8, delay: i * 0.04, ease: 'easeOut' }}
            />
          ))}
        </div>
      </div>

      {/* Bottom gradient bar */}
      <div className="h-[1px] bg-gradient-to-r from-purple-500/0 via-purple-400/40 to-purple-500/0" />
    </div>
  </motion.div>
);

/* Shimmer button wrapper */
const ShimmerButton: React.FC<{ children: React.ReactNode; to: string; className?: string; style?: React.CSSProperties }> = ({ children, to, className = '', style }) => (
  <Link to={to} className={`relative inline-flex items-center gap-2 overflow-hidden font-bold rounded-xl ${className}`} style={style}>
    {/* Shimmer sweep */}
    <motion.span
      className="absolute inset-0 block"
      style={{
        background: 'linear-gradient(110deg, transparent 20%, rgba(255,255,255,0.22) 50%, transparent 80%)',
        skewX: '-15deg',
      }}
      animate={{ x: ['-150%', '250%'] }}
      transition={{ duration: 2.2, repeat: Infinity, repeatDelay: 2, ease: 'easeInOut' }}
    />
    <span className="relative flex items-center gap-2">{children}</span>
  </Link>
);

const Hero: React.FC = () => {
  const scrollToDemo = () => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });

  return (
    <section className="relative min-h-screen flex items-center pt-28 pb-24 overflow-hidden">

      {/* ── Dot grid ── */}
      <div
        className="absolute inset-0 opacity-50 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(rgba(99,102,241,0.12) 1px, transparent 1px)',
          backgroundSize: '28px 28px',
        }}
      />

      {/* ── Orbs (large, vivid) ── */}
      <div className="absolute -top-40 -left-40 w-[700px] h-[700px] bg-indigo-600/30 rounded-full blur-[130px] pointer-events-none" />
      <div className="absolute top-1/4 -right-32 w-[600px] h-[600px] bg-purple-600/25 rounded-full blur-[110px] pointer-events-none" />
      <div className="absolute -bottom-32 left-1/3 w-[500px] h-[500px] bg-emerald-600/18 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 w-full relative">
        <div className="grid lg:grid-cols-2 gap-14 items-center">

          {/* ── Left: Copy ── */}
          <div className="space-y-8">

            {/* Glowing badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full text-sm font-semibold"
              style={{
                background: 'rgba(52,211,153,0.08)',
                border: '1px solid rgba(52,211,153,0.3)',
                color: '#34d399',
                boxShadow: '0 0 24px rgba(52,211,153,0.2), inset 0 0 12px rgba(52,211,153,0.05)',
              }}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse inline-block" />
              MS Data Science Capstone · University of New Haven 2026
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, delay: 0.1 }}
              className="text-6xl sm:text-7xl lg:text-8xl font-black leading-[0.95] tracking-tight text-white"
            >
              Your AI{' '}
              <span
                className="bg-clip-text text-transparent"
                style={{ backgroundImage: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 40%, #34d399 100%)' }}
              >
                Job Application
              </span>{' '}
              Assistant
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg sm:text-xl text-white/50 leading-relaxed max-w-lg"
            >
              Find, apply, and track jobs automatically using AI agents — working around the clock so you don't have to.
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-wrap gap-4"
            >
              {/* Primary shimmer button */}
              <motion.div
                whileHover={{ scale: 1.03, y: -2 }}
                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              >
                <ShimmerButton
                  to="/app"
                  className="text-white px-8 py-4 text-base"
                  style={{
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    boxShadow: '0 4px 24px rgba(99,102,241,0.35)',
                  } as React.CSSProperties}
                >
                  Get Started Free
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </ShimmerButton>
              </motion.div>

              {/* Ghost button with gradient border */}
              <motion.button
                onClick={scrollToDemo}
                whileHover={{ scale: 1.03, y: -2 }}
                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                className="relative inline-flex items-center gap-2.5 px-8 py-4 text-base font-semibold text-white/80 rounded-xl overflow-hidden"
                style={{
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.12)',
                }}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
                Watch Demo
              </motion.button>
            </motion.div>

            {/* Social proof */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="flex items-center gap-4 pt-2"
            >
              <div className="flex -space-x-2.5">
                {[
                  'from-blue-400 to-indigo-500',
                  'from-emerald-400 to-cyan-500',
                  'from-pink-400 to-purple-500',
                ].map((g, i) => (
                  <div
                    key={i}
                    className={`w-9 h-9 rounded-full bg-gradient-to-br ${g} border-2 border-[#050510] flex items-center justify-center text-xs font-bold`}
                  >
                    {['A', 'M', 'S'][i]}
                  </div>
                ))}
              </div>
              <div>
                <p className="text-sm text-white/50">
                  <span className="text-white font-semibold">500+</span> job seekers automated their search
                </p>
                <div className="flex gap-0.5 mt-0.5">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  ))}
                  <span className="text-white/30 text-xs ml-1">5.0</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* ── Right: Mock Dashboard ── */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.75, delay: 0.2, ease: 'easeOut' }}
          >
            <MockDashboard />
          </motion.div>

        </div>
      </div>
    </section>
  );
};

export default Hero;
