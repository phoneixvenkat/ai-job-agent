import React from 'react';
import { motion } from 'framer-motion';

interface ApplicationRow {
  company: string;
  role: string;
  status: string;
  score: number;
  statusColor: string;
  scoreColor: string;
}

const rows: ApplicationRow[] = [
  { company: 'Google', role: 'ML Engineer', status: 'Interview', score: 92, statusColor: 'text-yellow-400', scoreColor: 'text-emerald-400' },
  { company: 'Stripe', role: 'Data Scientist', status: 'Applied', score: 88, statusColor: 'text-blue-400', scoreColor: 'text-blue-400' },
  { company: 'OpenAI', role: 'AI Researcher', status: 'In Review', score: 78, statusColor: 'text-purple-400', scoreColor: 'text-purple-400' },
  { company: 'Anthropic', role: 'ML Engineer', status: 'Offer ✓', score: 95, statusColor: 'text-emerald-400', scoreColor: 'text-emerald-400' },
];

const bars = [
  { label: 'LinkedIn', value: 95, color: 'from-cyan-400 to-blue-400' },
  { label: 'Greenhouse', value: 78, color: 'from-indigo-400 to-purple-400' },
  { label: 'Remotive', value: 45, color: 'from-emerald-400 to-cyan-400' },
  { label: 'Lever', value: 40, color: 'from-pink-400 to-purple-400' },
];

const DashboardMock: React.FC = () => (
  <div className="relative">
    <div className="absolute inset-0 bg-gradient-to-br from-purple-500/15 to-cyan-500/15 rounded-3xl blur-2xl -z-10" />
    <div className="bg-white/[0.04] backdrop-blur-xl border border-white/[0.08] rounded-2xl p-6 space-y-5 shadow-2xl">

      {/* Application table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-white text-sm font-semibold">Application Tracker</span>
          <span className="text-emerald-400 text-xs font-mono">42 Active</span>
        </div>
        <div className="space-y-0">
          <div className="grid grid-cols-4 text-[10px] text-white/30 uppercase tracking-widest pb-2 border-b border-white/[0.06]">
            <span>Company</span>
            <span>Role</span>
            <span>Status</span>
            <span>Score</span>
          </div>
          {rows.map((r, i) => (
            <div
              key={r.company}
              className={`grid grid-cols-4 text-xs py-2.5 ${i < rows.length - 1 ? 'border-b border-white/[0.04]' : ''}`}
            >
              <span className="text-white font-medium">{r.company}</span>
              <span className="text-white/50 truncate pr-2">{r.role}</span>
              <span className={r.statusColor}>{r.status}</span>
              <span className={`${r.scoreColor} font-bold`}>{r.score}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Platform bars */}
      <div>
        <div className="text-white text-sm font-semibold mb-3">Platform Performance</div>
        <div className="space-y-2.5">
          {bars.map(({ label, value, color }) => (
            <div key={label}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-white/50">{label}</span>
                <span className="text-white">{value} jobs</span>
              </div>
              <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: `${value}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
                  className={`h-full bg-gradient-to-r ${color} rounded-full`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  </div>
);

const Demo: React.FC = () => (
  <section id="demo" className="relative py-32 lg:py-40 overflow-hidden">
    <div className="absolute top-1/2 right-0 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none -translate-y-1/2" />

    <div className="max-w-7xl mx-auto px-6">
      <div className="grid lg:grid-cols-2 gap-16 items-center">

        {/* Left: copy */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.65 }}
          className="space-y-7"
        >
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-4 py-1.5 rounded-full text-sm font-medium">
            Live Dashboard
          </div>
          <h2 className="text-5xl sm:text-6xl font-black text-white leading-tight">
            Every application,{' '}
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: 'linear-gradient(135deg, #22d3ee, #a78bfa)' }}
            >
              fully in view
            </span>
          </h2>
          <p className="text-white/50 text-lg leading-relaxed">
            A real-time command center showing every job you've applied to, your fit score, interview status, and platform analytics — all in one clean dashboard.
          </p>

          <div className="space-y-4">
            {[
              { icon: '📈', title: 'Fit Score Analytics', desc: 'AI match scores per job help you focus on roles you\'ll actually land.' },
              { icon: '🗂️', title: 'Full Application History', desc: 'Every application logged to MySQL with timestamps and status updates.' },
              { icon: '🔔', title: 'Smart Email Alerts', desc: 'Notified the moment an email looks like an interview invitation.' },
            ].map(({ icon, title, desc }) => (
              <div key={title} className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-lg flex-shrink-0">
                  {icon}
                </div>
                <div>
                  <div className="font-semibold text-white text-sm mb-0.5">{title}</div>
                  <div className="text-white/50 text-sm">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right: dashboard mock */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.65, delay: 0.1 }}
        >
          <DashboardMock />
        </motion.div>

      </div>
    </div>
  </section>
);

export default Demo;
