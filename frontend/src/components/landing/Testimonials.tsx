import React from 'react';
import { motion, type Variants } from 'framer-motion';

interface Testimonial {
  quote: string;
  name: string;
  role: string;
  initials: string;
  gradient: string;
}

const testimonials: Testimonial[] = [
  {
    quote: 'I was spending 3 hours a day on job applications. JobPilot AI does it all while I sleep. Landed 4 interviews in my first week of using it.',
    name: 'Arjun Kapoor',
    role: 'Data Scientist @ Stripe',
    initials: 'AK',
    gradient: 'from-blue-400 to-purple-500',
  },
  {
    quote: 'The fit scoring is insanely accurate. I stopped wasting time on roles I\'d never get and focused only on the ones that matched my profile.',
    name: 'Maya Rodriguez',
    role: 'ML Engineer @ Anthropic',
    initials: 'MR',
    gradient: 'from-emerald-400 to-cyan-500',
  },
  {
    quote: 'Privacy was my main concern with other tools. JobPilot runs entirely on my own machine — no one else touches my resume or email. Game changer.',
    name: 'Sana Kim',
    role: 'AI Researcher @ OpenAI',
    initials: 'SK',
    gradient: 'from-pink-400 to-purple-500',
  },
];

const containerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' as const } },
};

const Testimonials: React.FC = () => (
  <section id="testimonials" className="relative py-32 lg:py-40 overflow-hidden">
    <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-600/8 rounded-full blur-3xl pointer-events-none" />

    <div className="max-w-7xl mx-auto px-6">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-xl mx-auto mb-14"
      >
        <h2 className="text-5xl sm:text-6xl font-black text-white mb-3">
          Loved by job seekers{' '}
          <span
            className="bg-clip-text text-transparent"
            style={{ backgroundImage: 'linear-gradient(135deg, #818cf8, #34d399)' }}
          >
            worldwide
          </span>
        </h2>
      </motion.div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-80px' }}
        className="grid md:grid-cols-3 gap-5"
      >
        {testimonials.map((t) => (
          <motion.div
            key={t.name}
            variants={cardVariants}
            whileHover={{ y: -4 }}
            className="bg-gradient-to-br from-white/[0.05] to-white/[0.02] border border-white/[0.07] rounded-2xl p-6 flex flex-col"
          >
            {/* Stars */}
            <div className="flex gap-0.5 mb-4">
              {[...Array(5)].map((_, i) => (
                <svg key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
              ))}
            </div>

            {/* Quote */}
            <p className="text-white/60 text-sm leading-relaxed flex-1 mb-5">
              "{t.quote}"
            </p>

            {/* Avatar + name */}
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.gradient} flex items-center justify-center text-sm font-bold text-white flex-shrink-0`}>
                {t.initials}
              </div>
              <div>
                <div className="text-white font-semibold text-sm">{t.name}</div>
                <div className="text-white/40 text-xs">{t.role}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  </section>
);

export default Testimonials;
