'use client';

import { motion } from 'framer-motion';

const features = [
  {
    icon: '📊',
    title: 'Real-Time Dashboard',
    description: 'See your complete financial picture at a glance with beautiful visualizations and live updates.',
    gradient: 'from-purple-500 to-indigo-500',
    delay: 0,
  },
  {
    icon: '💳',
    title: 'Smart Transactions',
    description: 'Track every income and expense with intelligent categorization and recurring payment support.',
    gradient: 'from-blue-500 to-cyan-500',
    delay: 0.1,
  },
  {
    icon: '🎯',
    title: 'Budget Mastery',
    description: 'Set spending limits by category and get smart alerts before you overspend.',
    gradient: 'from-pink-500 to-rose-500',
    delay: 0.2,
  },
  {
    icon: '📈',
    title: 'Analytics & Trends',
    description: 'Beautiful charts reveal your spending patterns and help you make smarter decisions.',
    gradient: 'from-amber-500 to-orange-500',
    delay: 0.3,
  },
  {
    icon: '🤖',
    title: 'AI Assistant',
    description: 'Get personalized financial advice and insights from our intelligent chatbot.',
    gradient: 'from-emerald-500 to-teal-500',
    delay: 0.4,
  },
  {
    icon: '🌙',
    title: 'Beautiful Design',
    description: 'Stunning glassmorphic interface with dark mode support. Finance has never looked this good.',
    gradient: 'from-violet-500 to-purple-500',
    delay: 0.5,
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

export function FeatureShowcase() {
  return (
    <section className="relative px-6 py-32 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-500/5 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <motion.span
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-block px-4 py-2 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-semibold mb-6"
          >
            Powerful Features
          </motion.span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Everything You Need to
            <br />
            <span className="bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent">
              Master Your Money
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            A complete suite of tools designed to help you track, analyze, and optimize your finances.
          </p>
        </motion.div>

        {/* Feature Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={cardVariants}
              whileHover={{ scale: 1.03, y: -8 }}
              className="group relative"
            >
              {/* Glow effect on hover */}
              <div className={`absolute inset-0 rounded-3xl bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500`} />

              {/* Card */}
              <div className="relative h-full rounded-3xl bg-white/50 dark:bg-gray-900/50 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 p-8 shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden">
                {/* Gradient accent */}
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${feature.gradient} opacity-10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:opacity-30 transition-opacity duration-500`} />

                {/* Content */}
                <div className="relative z-10">
                  {/* Icon */}
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} mb-6 shadow-lg`}
                  >
                    <span className="text-3xl">{feature.icon}</span>
                  </motion.div>

                  {/* Title */}
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                    {feature.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>

                  {/* Learn more link */}
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    whileHover={{ x: 0 }}
                    className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  >
                    <span className={`text-sm font-semibold bg-gradient-to-r ${feature.gradient} bg-clip-text text-transparent flex items-center gap-1`}>
                      Learn more
                      <span>→</span>
                    </span>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
