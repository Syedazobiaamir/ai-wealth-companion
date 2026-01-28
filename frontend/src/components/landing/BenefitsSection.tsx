'use client';

import { motion } from 'framer-motion';

const benefits = [
  {
    number: '01',
    title: 'Stop Living Paycheck to Paycheck',
    description: 'Finally understand where your money goes. Track every transaction automatically and see your complete financial picture in seconds.',
    image: '💸',
    stats: { value: '67%', label: 'of users save more' },
  },
  {
    number: '02',
    title: 'Crush Your Budget Goals',
    description: 'Set realistic spending limits for each category. Get smart alerts before you overspend, not after the damage is done.',
    image: '🎯',
    stats: { value: '3x', label: 'faster budget tracking' },
  },
  {
    number: '03',
    title: 'Make Smarter Financial Decisions',
    description: 'Beautiful analytics reveal your spending patterns. Discover hidden money drains and opportunities to save more every month.',
    image: '🧠',
    stats: { value: '$400', label: 'avg monthly savings' },
  },
  {
    number: '04',
    title: 'AI That Actually Understands You',
    description: 'Our intelligent assistant learns your habits and provides personalized advice. Like having a financial advisor in your pocket.',
    image: '🤖',
    stats: { value: '24/7', label: 'instant advice' },
  },
];

export function BenefitsSection() {
  return (
    <section className="relative px-6 py-32 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 via-white to-blue-50/50 dark:from-purple-950/20 dark:via-gray-950 dark:to-blue-950/20" />

      <div className="relative max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <span className="inline-block px-4 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-semibold mb-6">
            Why Choose Us
          </span>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Transform Your
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-purple-500 bg-clip-text text-transparent">
              Financial Life
            </span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Join thousands who have taken control of their money with our intelligent platform.
          </p>
        </motion.div>

        {/* Benefits List */}
        <div className="space-y-24">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.number}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className={`flex flex-col ${
                index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'
              } items-center gap-12 lg:gap-20`}
            >
              {/* Content */}
              <div className="flex-1 space-y-6">
                <motion.span
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  className="inline-block text-7xl font-bold bg-gradient-to-r from-purple-200 to-blue-200 dark:from-purple-900/50 dark:to-blue-900/50 bg-clip-text text-transparent"
                >
                  {benefit.number}
                </motion.span>
                <h3 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
                  {benefit.title}
                </h3>
                <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed">
                  {benefit.description}
                </p>

                {/* Stat badge */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="inline-flex items-center gap-4 px-6 py-4 rounded-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg"
                >
                  <span className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent">
                    {benefit.stats.value}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {benefit.stats.label}
                  </span>
                </motion.div>
              </div>

              {/* Visual */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="flex-1 w-full max-w-md"
              >
                <div className="relative">
                  {/* Glow */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-3xl blur-3xl" />

                  {/* Card */}
                  <div className="relative rounded-3xl bg-gradient-to-br from-white/80 to-white/40 dark:from-gray-800/80 dark:to-gray-900/40 backdrop-blur-2xl border border-white/40 dark:border-gray-700/40 p-12 shadow-2xl">
                    {/* Large Icon */}
                    <motion.div
                      animate={{
                        y: [0, -10, 0],
                        rotate: [0, 5, 0, -5, 0],
                      }}
                      transition={{
                        duration: 5,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      className="text-8xl text-center mb-6"
                    >
                      {benefit.image}
                    </motion.div>

                    {/* Decorative elements */}
                    <div className="flex justify-center gap-3">
                      {[...Array(4)].map((_, i) => (
                        <motion.div
                          key={i}
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.5, 1, 0.5],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                          className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
