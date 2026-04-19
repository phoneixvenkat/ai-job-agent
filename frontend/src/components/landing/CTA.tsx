import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const CTA: React.FC = () => (
  <section id="cta" className="relative py-40 overflow-hidden">

    {/* ── Animated gradient orbs ── */}
    <motion.div
      className="absolute w-[600px] h-[600px] rounded-full pointer-events-none"
      style={{ left: '50%', top: '50%', filter: 'blur(80px)', transform: 'translate(-50%, -50%)' }}
      animate={{
        background: [
          'radial-gradient(circle, rgba(99,102,241,0.22) 0%, transparent 70%)',
          'radial-gradient(circle, rgba(168,85,247,0.28) 0%, transparent 70%)',
          'radial-gradient(circle, rgba(52,211,153,0.18) 0%, transparent 70%)',
          'radial-gradient(circle, rgba(99,102,241,0.22) 0%, transparent 70%)',
        ],
      }}
      transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
    />
    <div className="absolute -top-32 left-1/4 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
    <div className="absolute -bottom-32 right-1/4 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl pointer-events-none" />

    {/* ── Dot grid ── */}
    <div
      className="absolute inset-0 opacity-30 pointer-events-none"
      style={{
        backgroundImage: 'radial-gradient(rgba(99,102,241,0.15) 1px, transparent 1px)',
        backgroundSize: '28px 28px',
      }}
    />

    <div className="max-w-3xl mx-auto px-6 text-center relative z-10">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
      >
        {/* Glowing badge */}
        <div
          className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full text-sm font-semibold mb-10"
          style={{
            background: 'rgba(52,211,153,0.08)',
            border: '1px solid rgba(52,211,153,0.3)',
            color: '#34d399',
            boxShadow: '0 0 30px rgba(52,211,153,0.2)',
          }}
        >
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse inline-block" />
          Ready to automate your career
        </div>

        {/* Headline */}
        <h2 className="text-6xl sm:text-7xl lg:text-8xl font-black text-white leading-[0.95] mb-6">
          Stop applying{' '}
          <span
            className="bg-clip-text text-transparent"
            style={{ backgroundImage: 'linear-gradient(135deg, #818cf8, #a78bfa, #34d399)' }}
          >
            manually.
          </span>
        </h2>

        <p className="text-xl text-white/45 leading-relaxed mb-3">
          Let 6 AI agents find, apply, and track jobs while you focus on what actually matters.
        </p>
        <p className="text-sm text-white/25 mb-12">
          Free · Open Source · Runs locally · No data leaves your machine
        </p>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">

          {/* Primary — layered glow button */}
          <motion.div
            animate={{
              boxShadow: [
                '0 0 20px rgba(99,102,241,0.4), 0 0 40px rgba(99,102,241,0.2)',
                '0 0 35px rgba(168,85,247,0.5), 0 0 70px rgba(168,85,247,0.25)',
                '0 0 20px rgba(99,102,241,0.4), 0 0 40px rgba(99,102,241,0.2)',
              ],
            }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            className="rounded-xl"
          >
            <motion.div whileHover={{ scale: 1.04, y: -2 }} transition={{ type: 'spring', stiffness: 400, damping: 18 }}>
              <Link
                to="/app"
                className="relative inline-flex items-center gap-2.5 px-10 py-4 rounded-xl text-lg font-bold text-white overflow-hidden"
                style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}
              >
                {/* Shimmer */}
                <motion.span
                  className="absolute inset-0"
                  style={{
                    background: 'linear-gradient(110deg, transparent 20%, rgba(255,255,255,0.2) 50%, transparent 80%)',
                  }}
                  animate={{ x: ['-150%', '250%'] }}
                  transition={{ duration: 2.5, repeat: Infinity, repeatDelay: 1.5, ease: 'easeInOut' }}
                />
                <span className="relative">🚀 Launch JobPilot AI</span>
              </Link>
            </motion.div>
          </motion.div>

          {/* Ghost button */}
          <motion.a
            href="https://github.com/phoneixvenkat/ai-job-agent"
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.04, y: -2 }}
            transition={{ type: 'spring', stiffness: 400, damping: 18 }}
            className="inline-flex items-center justify-center gap-2.5 px-10 py-4 rounded-xl text-lg font-semibold text-white/70 hover:text-white transition-colors"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.1)',
            }}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
            </svg>
            View on GitHub
          </motion.a>
        </div>

        {/* Trust badges */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-6">
          {['🔒 Privacy-first', '⚡ Runs locally', '🆓 100% free', '📖 Open source'].map((badge) => (
            <span key={badge} className="text-sm text-white/25 font-medium">{badge}</span>
          ))}
        </div>
      </motion.div>
    </div>
  </section>
);

export default CTA;
