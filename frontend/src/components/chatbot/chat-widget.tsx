'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { aiApi } from '@/lib/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: { label: string; action: string }[];
}

// Conversation state for API
let conversationId: string | undefined;

const QUICK_ACTIONS = [
  { label: 'Summary', query: 'Give me a summary of my finances', icon: 'chart' },
  { label: 'Budget', query: 'How are my budgets doing?', icon: 'wallet' },
  { label: 'Tips', query: 'Give me saving tips', icon: 'lightbulb' },
  { label: 'Trends', query: 'Show my spending trends', icon: 'trending' },
];

const AI_RESPONSES: Record<string, { content: string; actions?: { label: string; action: string }[] }> = {
  summary: {
    content: "📊 **Your Financial Summary (January 2026)**\n\n• Total Income: $10,500\n• Total Expenses: $4,700\n• Net Balance: +$5,800\n\nYou're doing great! You've saved 55% of your income this month. Keep it up! 🎉",
    actions: [
      { label: 'View Dashboard', action: '/dashboard' },
      { label: 'See Transactions', action: '/transactions' },
    ],
  },
  budget: {
    content: "⚠️ **Budget Alert!**\n\nSeveral budgets are over limit:\n\n• 🍔 Food: 178% ($1,070 / $600)\n• 🏠 Rent: 185% ($2,400 / $1,300)\n• 🎬 Entertainment: 130% ($130 / $100)\n\nConsider reviewing your spending or adjusting your budget limits.",
    actions: [
      { label: 'Manage Budgets', action: '/budgets' },
    ],
  },
  tips: {
    content: "💡 **Personalized Saving Tips**\n\n1. **Food Budget**: You're $470 over. Try meal prepping to reduce restaurant expenses.\n\n2. **Entertainment**: Cancel unused subscriptions. You could save ~$30/month.\n\n3. **50/30/20 Rule**: Aim for 50% needs, 30% wants, 20% savings.\n\n4. **Automate Savings**: Set up automatic transfers to savings on payday.\n\nWant me to help you create a savings plan?",
  },
  trends: {
    content: "📈 **Spending Trends**\n\nYour top spending categories this month:\n\n1. 🏠 Rent: $2,400 (51%)\n2. 🍔 Food: $1,070 (23%)\n3. 🛒 Shopping: $400 (9%)\n4. 🚗 Transportation: $240 (5%)\n\nCompared to typical months, your food spending is higher. Consider cooking more at home!",
    actions: [
      { label: 'View Analytics', action: '/analytics' },
    ],
  },
  default: {
    content: "I'm your AI financial assistant! I can help you with:\n\n• 📊 Financial summaries\n• 💰 Budget tracking\n• 💡 Saving tips\n• 📈 Spending analysis\n\nTry asking me something or use the quick actions below!",
  },
};

function getAIResponse(query: string): { content: string; actions?: { label: string; action: string }[] } {
  const lowerQuery = query.toLowerCase();

  if (lowerQuery.includes('summary') || lowerQuery.includes('overview') || lowerQuery.includes('finances')) {
    return AI_RESPONSES.summary;
  }
  if (lowerQuery.includes('budget') || lowerQuery.includes('limit') || lowerQuery.includes('spending limit')) {
    return AI_RESPONSES.budget;
  }
  if (lowerQuery.includes('tip') || lowerQuery.includes('save') || lowerQuery.includes('advice')) {
    return AI_RESPONSES.tips;
  }
  if (lowerQuery.includes('trend') || lowerQuery.includes('spending') || lowerQuery.includes('category')) {
    return AI_RESPONSES.trends;
  }
  if (lowerQuery.includes('hello') || lowerQuery.includes('hi') || lowerQuery.includes('hey')) {
    return { content: "Hello! 👋 I'm your AI financial assistant. How can I help you today?\n\nYou can ask me about your financial summary, budgets, saving tips, or spending trends!" };
  }
  if (lowerQuery.includes('thank')) {
    return { content: "You're welcome! 😊 Feel free to ask if you need anything else. I'm here to help you manage your finances better!" };
  }

  return {
    content: "I understand you're asking about: \"" + query + "\"\n\nI can help you with financial summaries, budget tracking, saving tips, and spending analysis. Try one of the quick actions below or rephrase your question!",
  };
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "👋 Hi! I'm your AI financial assistant. I can help you understand your finances, track budgets, and provide personalized tips.\n\nWhat would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (query?: string) => {
    const messageText = query || inputValue;
    if (!messageText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Try to use the real AI API
      const response = await aiApi.query(messageText, { conversation_id: conversationId });

      // Check if we got a real AI response (not the stub)
      if (response.data.confidence > 0) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.answer,
          timestamp: new Date(),
          actions: response.data.suggested_actions?.map(a => ({
            label: a.label,
            action: a.action === 'view_dashboard' ? '/dashboard' : `/${a.action}`,
          })),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        // Fall back to local responses (Phase III not yet active)
        const localResponse = getAIResponse(messageText);
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: localResponse.content,
          timestamp: new Date(),
          actions: localResponse.actions,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch {
      // API call failed, use local fallback
      const localResponse = getAIResponse(messageText);
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: localResponse.content,
        timestamp: new Date(),
        actions: localResponse.actions,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleAction = (action: string) => {
    window.location.href = action;
  };

  return (
    <>
      {/* Chat Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'fixed bottom-24 right-6 lg:bottom-6 z-50',
          'w-14 h-14 rounded-full',
          'bg-gradient-to-r from-purple-600 to-blue-500 text-white',
          'flex items-center justify-center',
          'shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50',
          'transition-shadow'
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Open chat"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.svg
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </motion.svg>
          ) : (
            <motion.svg
              key="chat"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </motion.svg>
          )}
        </AnimatePresence>

        {/* Notification dot */}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />
        )}
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              'fixed bottom-40 right-6 lg:bottom-24 z-50',
              'w-80 sm:w-96 h-[32rem]',
              'bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl',
              'rounded-3xl shadow-2xl shadow-purple-500/20',
              'border border-white/30 dark:border-gray-700/50',
              'flex flex-col overflow-hidden'
            )}
          >
            {/* Header */}
            <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-600 to-blue-500 text-white">
              <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">AI Assistant</h3>
                <p className="text-xs text-white/80 flex items-center gap-1">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  Online
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/10 rounded-xl transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    'max-w-[85%]',
                    message.role === 'user' ? 'ml-auto' : 'mr-auto'
                  )}
                >
                  <div
                    className={cn(
                      'p-3 rounded-2xl',
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-br-md'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-bl-md'
                    )}
                  >
                    <p className="text-sm whitespace-pre-line">{message.content}</p>
                  </div>

                  {/* Action buttons */}
                  {message.actions && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {message.actions.map((action, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleAction(action.action)}
                          className="text-xs px-3 py-1.5 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 text-gray-500"
                >
                  <div className="flex gap-1 p-3 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {QUICK_ACTIONS.map((action, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(action.query)}
                    className="flex-shrink-0 flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-gray-100 dark:bg-gray-800 text-slate-700 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 hover:text-purple-700 dark:hover:text-purple-300 transition-colors duration-200 whitespace-nowrap cursor-pointer"
                  >
                    {action.icon === 'chart' && (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    )}
                    {action.icon === 'wallet' && (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    )}
                    {action.icon === 'lightbulb' && (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    )}
                    {action.icon === 'trending' && (
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    )}
                    {action.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask me anything..."
                  className={cn(
                    'flex-1 px-4 py-2.5 rounded-xl',
                    'bg-gray-100 dark:bg-gray-800',
                    'text-gray-900 dark:text-white',
                    'placeholder:text-gray-500',
                    'focus:outline-none focus:ring-2 focus:ring-purple-500/50',
                    'transition-all'
                  )}
                />
                <motion.button
                  onClick={() => handleSend()}
                  disabled={!inputValue.trim() || isTyping}
                  className={cn(
                    'p-2.5 rounded-xl',
                    'bg-gradient-to-r from-purple-600 to-blue-500 text-white',
                    'disabled:opacity-50 disabled:cursor-not-allowed',
                    'shadow-lg shadow-purple-500/25'
                  )}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                    />
                  </svg>
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
