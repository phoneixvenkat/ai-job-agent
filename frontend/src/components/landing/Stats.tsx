import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';

interface Stat {
  value: number;
  suffix: string;
  label: string;
  sub: string;
  gradient: string;
  glow: string;
}

const stats: Stat[] = [
  {
    value: 500,
    suffix: '+',
    label: 'Jobs Found',
    sub: 'per session',
    gradient: 'linear-gradient(135deg, #818cf8, #a78bfa)',
    glow: '0 0 40px rgba(99,102,241,0.35)',
  },
  {
    value: 30,
    suffix: 's',
    label: 'Cover Letters',
    sub: 'generated in',
    gradient: 'linear-gradient(135deg, #34d399, #22d3ee)',
    glow: '0 0 40px rgba(52,211,153,0.35)',
  },
  {
    value: 6,
    suffix: '',
    label: 'Platforms',
    sub: 'scanned simultaneously',
    gradient: 'linear-gradient(135deg, #c084fc, #f472b6)',
    glow: '0 0 40px rgba(192,132,252,0.35)',
  },
  {
    value: 95,
    suffix: '%',
    label: 'Automation Level',
    sub: 'end-to-end',
    gradient: 'linear-gradient(135deg, #22d3ee, #6366f1)',
    glow: '0 0 40px rgba(34,211,238,0.35)',
  },
];

function useCountUp(end: number, duration: number, trigger: boolean): number {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!trigger) return;
    const startTime = Date.now();
    const timer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(end * eased));
      if (progress >= 1) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [trigger, end, duration]);
  return count;
}

interface StatCardProps {
  stat: Stat;
  triggered: boolean;
  delay: number;
}

const StatCard: React.FC<StatCardProps> = ({ stat, triggered, delay }) => {
  const count = useCountUp(stat.value, 2000, triggered);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -4, boxShadow: stat.glow }}
      className="relative rounded-2xl p-6 sm:p-8 text-center cursor-default"
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.07)',
        transition: 'box-shadow 0.3s ease, transform 0.3s ease',
      }}
    >
      {/* Number with glow */}
      <div className="relative inline-block">
        <div
          className="text-6xl sm:text-7xl font-black leading-none mb-0.5 bg-clip-text text-transparent"
          style={{ backgroundImage: stat.gradient }}
        >
          {count}{stat.suffix}
        </div>
        {/* Glow blur behind number */}
        <div
          className="absolute inset-0 -z-10 blur-xl opacity-40"
          style={{
            background: stat.gradient,
            filter: 'blur(24px)',
            transform: 'scale(0.8) translateY(8px)',
          }}
        />
      </div>

      <div className="text-white font-semibold text-base mt-3 mb-0.5">{stat.label}</div>
      <div className="text-white/35 text-sm">{stat.sub}</div>
    </motion.div>
  );
};

const Stats: React.FC = () => {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <section id="stats" className="relative py-32 lg:py-40 overflow-hidden">
      {/* Top accent glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-64 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl sm:text-6xl font-black text-white leading-tight">
            Numbers that{' '}
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: 'linear-gradient(135deg, #818cf8, #a78bfa, #34d399)' }}
            >
              prove it works
            </span>
          </h2>
          <p className="text-white/40 text-lg mt-4">Real metrics from the JobPilot AI pipeline.</p>
        </motion.div>

        <div ref={ref} className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {stats.map((stat, i) => (
            <StatCard key={stat.label} stat={stat} triggered={inView} delay={i * 0.08} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default Stats;
