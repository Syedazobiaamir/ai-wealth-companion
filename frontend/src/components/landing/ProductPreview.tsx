'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';

const previewCards = [
  {
    title: 'Smart Dashboard',
    description: 'Your complete financial overview',
    gradient: 'from-purple-600 to-indigo-600',
    content: (
      <div className="space-y-4">
        {/* Mini stat cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 rounded-xl bg-white/60 dark:bg-gray-800/60">
            <div className="text-xs text-gray-500">Income</div>
            <div className="text-lg font-bold text-green-500">+$8,400</div>
          </div>
          <div className="p-3 rounded-xl bg-white/60 dark:bg-gray-800/60">
            <div className="text-xs text-gray-500">Expenses</div>
            <div className="text-lg font-bold text-red-500">-$3,200</div>
          </div>
          <div className="p-3 rounded-xl bg-white/60 dark:bg-gray-800/60">
            <div className="text-xs text-gray-500">Savings</div>
            <div className="text-lg font-bold text-blue-500">$5,200</div>
          </div>
        </div>
        {/* Mini chart */}
        <div className="h-24 rounded-xl bg-gradient-to-r from-purple-500/20 to-blue-500/20 flex items-end justify-around p-3">
          {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
            <motion.div
              key={i}
              initial={{ height: 0 }}
              whileInView={{ height: `${h}%` }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="w-4 rounded-t-lg bg-gradient-to-t from-purple-500 to-blue-400"
            />
          ))}
        </div>
      </div>
    ),
  },
  {
    title: 'Budget Tracking',
    description: 'Never overspend again',
    gradient: 'from-pink-600 to-rose-600',
    content: (
      <div className="space-y-3">
        {[
          { name: 'Food', spent: 450, limit: 600, emoji: '🍔' },
          { name: 'Transport', spent: 180, limit: 200, emoji: '🚗' },
          { name: 'Shopping', spent: 320, limit: 300, emoji: '🛍️' },
        ].map((budget, i) => (
          <div key={budget.name} className="p-3 rounded-xl bg-white/60 dark:bg-gray-800/60">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium flex items-center gap-2">
                {budget.emoji} {budget.name}
              </span>
              <span className={`text-xs font-bold ${budget.spent > budget.limit ? 'text-red-500' : 'text-gray-500'}`}>
                ${budget.spent}/${budget.limit}
              </span>
            </div>
            <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${Math.min((budget.spent / budget.limit) * 100, 100)}%` }}
                transition={{ delay: 0.3 + i * 0.1, duration: 0.8 }}
                className={`h-full rounded-full ${
                  budget.spent > budget.limit
                    ? 'bg-gradient-to-r from-red-500 to-rose-500'
                    : 'bg-gradient-to-r from-green-500 to-emerald-500'
                }`}
              />
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    title: 'AI Insights',
    description: 'Smart financial advice',
    gradient: 'from-emerald-600 to-teal-600',
    content: (
      <div className="space-y-3">
        <div className="p-4 rounded-xl bg-white/60 dark:bg-gray-800/60 border-l-4 border-emerald-500">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <div className="text-sm font-medium">Saving Opportunity</div>
              <div className="text-xs text-gray-500">You could save $120/mo on subscriptions</div>
            </div>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-white/60 dark:bg-gray-800/60 border-l-4 border-blue-500">
          <div className="flex items-start gap-3">
            <span className="text-2xl">📊</span>
            <div>
              <div className="text-sm font-medium">Spending Alert</div>
              <div className="text-xs text-gray-500">Food spending up 23% vs last month</div>
            </div>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-white/60 dark:bg-gray-800/60 border-l-4 border-purple-500">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <div className="text-sm font-medium">Goal Progress</div>
              <div className="text-xs text-gray-500">67% towards vacation fund goal</div>
            </div>
          </div>
        </div>
      </div>
    ),
  },
];

export function ProductPreview() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  });

  const x = useTransform(scrollYProgress, [0, 1], ['0%', '-15%']);

  return (
    <section ref={containerRef} className="relative py-32 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-50 via-purple-50/30 to-gray-50 dark:from-gray-950 dark:via-purple-950/10 dark:to-gray-950" />

      <div className="relative">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16 px-6"
        >
          <span className="inline-block px-4 py-2 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-sm font-semibold mb-6">
            Live Preview
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            See It In Action
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            A glimpse into the powerful features waiting for you
          </p>
        </motion.div>

        {/* Scrolling Preview Cards */}
        <motion.div style={{ x }} className="flex gap-8 px-8">
          {/* Spacer */}
          <div className="w-[20vw] flex-shrink-0" />

          {previewCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.2, duration: 0.6 }}
              whileHover={{ scale: 1.02, y: -10 }}
              className="w-[350px] flex-shrink-0"
            >
              {/* Glow */}
              <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} opacity-20 blur-3xl rounded-3xl`} />

              {/* Card */}
              <div className="relative rounded-3xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-2xl border border-white/40 dark:border-gray-700/40 shadow-2xl overflow-hidden">
                {/* Header */}
                <div className={`px-6 py-4 bg-gradient-to-r ${card.gradient} text-white`}>
                  <h3 className="text-lg font-bold">{card.title}</h3>
                  <p className="text-sm text-white/80">{card.description}</p>
                </div>

                {/* Content */}
                <div className="p-6">{card.content}</div>
              </div>
            </motion.div>
          ))}

          {/* Spacer */}
          <div className="w-[20vw] flex-shrink-0" />
        </motion.div>

        {/* Fade edges */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-50 dark:from-gray-950 to-transparent pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-50 dark:from-gray-950 to-transparent pointer-events-none" />
      </div>
    </section>
  );
}
