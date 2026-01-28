'use client';

import { motion } from 'framer-motion';

export function FloatingElements() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Main gradient orbs */}
      <motion.div
        className="absolute top-20 -left-20 w-[500px] h-[500px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(147,51,234,0.3) 0%, rgba(79,70,229,0.1) 50%, transparent 70%)',
        }}
        animate={{
          x: [0, 80, 0],
          y: [0, 40, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-20 -right-20 w-[600px] h-[600px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(59,130,246,0.3) 0%, rgba(147,51,234,0.1) 50%, transparent 70%)',
        }}
        animate={{
          x: [0, -60, 0],
          y: [0, -30, 0],
          scale: [1, 1.15, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full opacity-50"
        style={{
          background: 'radial-gradient(circle, rgba(236,72,153,0.15) 0%, rgba(147,51,234,0.1) 30%, transparent 60%)',
        }}
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
      />

      {/* Floating finance icons */}
      <motion.div
        className="absolute top-[15%] right-[15%] text-4xl opacity-60"
        animate={{
          y: [0, -20, 0],
          rotate: [0, 10, 0],
        }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
      >
        💳
      </motion.div>
      <motion.div
        className="absolute top-[25%] left-[10%] text-5xl opacity-50"
        animate={{
          y: [0, 25, 0],
          rotate: [0, -15, 0],
        }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
      >
        📊
      </motion.div>
      <motion.div
        className="absolute bottom-[30%] right-[8%] text-4xl opacity-60"
        animate={{
          y: [0, -15, 0],
          x: [0, 10, 0],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
      >
        💰
      </motion.div>
      <motion.div
        className="absolute bottom-[20%] left-[15%] text-3xl opacity-50"
        animate={{
          y: [0, 20, 0],
          rotate: [0, 20, 0],
        }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
      >
        📈
      </motion.div>
      <motion.div
        className="absolute top-[40%] right-[5%] text-3xl opacity-40"
        animate={{
          y: [0, -25, 0],
          x: [0, -15, 0],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
      >
        🎯
      </motion.div>
      <motion.div
        className="absolute top-[60%] left-[5%] text-4xl opacity-45"
        animate={{
          y: [0, 15, 0],
          rotate: [0, -10, 0],
        }}
        transition={{ duration: 5.5, repeat: Infinity, ease: 'easeInOut', delay: 3 }}
      >
        🏦
      </motion.div>

      {/* Sparkle particles */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-gradient-to-r from-purple-400 to-blue-400"
          style={{
            top: `${20 + Math.random() * 60}%`,
            left: `${10 + Math.random() * 80}%`,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.5,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}
