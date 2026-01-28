'use client';

import { motion } from 'framer-motion';

const stats = [
  { value: '10K+', label: 'Active Users', icon: '👥' },
  { value: '$5M+', label: 'Money Tracked', icon: '💰' },
  { value: '99.9%', label: 'Uptime', icon: '⚡' },
  { value: '4.9/5', label: 'User Rating', icon: '⭐' },
];

export function StatsBar() {
  return (
    <section className="relative px-6 py-16">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative"
        >
          {/* Gradient border wrapper */}
          <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 via-pink-500 to-blue-600 rounded-3xl opacity-75 blur-sm" />

          {/* Main card */}
          <div className="relative rounded-3xl bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl p-8 md:p-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="text-center"
                >
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className="inline-block text-3xl mb-2"
                  >
                    {stat.icon}
                  </motion.div>
                  <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
