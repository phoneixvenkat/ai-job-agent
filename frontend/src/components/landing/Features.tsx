import React from 'react';
import { motion, type Variants } from 'framer-motion';

interface Feature {
  icon: string;
  title: string;
  description: string;
  gradient: string;
}

const features: Feature[] = [
  {
    icon: '🔍',
    title: 'Automatic Job Search',
    description: 'Continuously scans 5+ platforms for roles matching your skills, experience, and salary target — no manual searching required.',
    gradient: 'from-indigo-500/20 to-blue-500/10',
  },
  {
    icon: '✨',
    title: 'Personalized Applications',
    description: 'Every resume and cover letter is uniquely crafted per role using LLM reasoning — not a template, but a targeted pitch.',
    gradient: 'from-purple-500/20 to-pink-500/10',
  },
  {
    icon: '📡',
    title: 'Smart Application Tracking',
    description: 'Real-time status across all applications — applied, reviewed, interviewed, or rejected — synced to MySQL and a live dashboard.',
    gradient: 'from-emerald-500/20 to-cyan-500/10',
  },
  {
    icon: '🧠',
    title: 'AI Adaptive Learning',
    description: 'Learns from your outcomes — which companies, titles, and platforms generate callbacks — and automatically adjusts recommendations.',
    gradient: 'from-orange-500/20 to-yellow-500/10',
  },
  {
    icon: '🔒',
    title: 'Privacy-First — Runs Locally',
    description: 'All LLM processing runs on your machine via Ollama. Your resume and personal data never leave your computer.',
    gradient: 'from-cyan-500/20 to-teal-500/10',
  },
];

const containerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.55, ease: 'easeOut' as const } },
};

const Features: React.FC = () => (
  <section id="features" className="relative py-32 lg:py-40 overflow-hidden">
    <div className="absolute top-1/2 left-0 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none -translate-y-1/2" />

    <div className="max-w-7xl mx-auto px-6">
      <div className="grid lg:grid-cols-2 gap-16 items-start">

        {/* Left: sticky copy */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="lg:sticky lg:top-32"
        >
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/20 text-purple-400 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
            Everything You Need
          </div>
          <h2 className="text-5xl sm:text-6xl font-black text-white leading-tight mb-6">
            Built for the modern{' '}
            <span
              className="bg-clip-text text-transparent"
              style={{ backgroundImage: 'linear-gradient(135deg, #a78bfa, #34d399)' }}
            >
              job seeker
            </span>
          </h2>
          <p className="text-white/50 text-lg leading-relaxed mb-8">
            JobPilot AI handles the entire pipeline — from discovery to offer — with no manual effort. You focus on interviews, we handle everything else.
          </p>

          {/* Mini stat row */}
          <div className="flex gap-8">
            <div>
              <div className="text-3xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">258+</div>
              <div className="text-white/40 text-sm mt-0.5">Jobs found per run</div>
            </div>
            <div className="w-px bg-white/10" />
            <div>
              <div className="text-3xl font-black bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">95%</div>
              <div className="text-white/40 text-sm mt-0.5">Automation level</div>
            </div>
          </div>
        </motion.div>

        {/* Right: feature list */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
          className="space-y-4"
        >
          {features.map((f) => (
            <motion.div
              key={f.title}
              variants={itemVariants}
              whileHover={{ x: 4 }}
              className={`bg-gradient-to-r ${f.gradient} border border-white/[0.07] rounded-2xl p-6 flex items-start gap-5 cursor-default transition-all`}
            >
              <div className="text-3xl flex-shrink-0 mt-0.5">{f.icon}</div>
              <div>
                <h3 className="text-white font-bold text-base mb-1.5">{f.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed">{f.description}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

      </div>
    </div>
  </section>
);

export default Features;
