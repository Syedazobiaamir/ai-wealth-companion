'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { aiApi } from '@/lib/api';
import { LanguageToggle } from '@/components/ai/language-toggle';
import { VoiceButton } from '@/components/ai/voice-button';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  content_ur?: string;
  timestamp: Date;
  actions?: { label: string; action: string }[];
  intent?: string;
  confidence?: number;
}

const QUICK_ACTIONS = [
  { label: 'Summary', query: 'Show my financial summary', icon: 'chart' },
  { label: 'Budget', query: 'How are my budgets doing?', icon: 'wallet' },
  { label: 'Tips', query: 'Analyze my spending and give tips', icon: 'lightbulb' },
  { label: 'Invest', query: 'Can I invest 50,000?', icon: 'trending' },
];

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI financial assistant. I can help you track expenses, manage budgets, analyze spending, and simulate investments.\n\nWhat would you like to do?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [language, setLanguage] = useState<string>('en');
  const [voiceTranscript, setVoiceTranscript] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('ai_language');
    if (saved) setLanguage(saved);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (query?: string, inputMethod: string = 'text') => {
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
    setVoiceTranscript('');
    setIsTyping(true);

    try {
      const response = await aiApi.chat(messageText, conversationId, language, inputMethod);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const aiMessage: ChatMessage = {
        id: response.message_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response || 'I could not process that request.',
        content_ur: response.response_ur,
        timestamp: new Date(),
        intent: response.intent,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleVoiceTranscript = useCallback((text: string, confidence: number) => {
    if (confidence >= 0.7) {
      handleSend(text, 'voice');
    } else {
      setVoiceTranscript(text);
      setInputValue(text);
    }
  }, [conversationId, language]);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
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
            <motion.svg key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </motion.svg>
          ) : (
            <motion.svg key="chat" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }} className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </motion.svg>
          )}
        </AnimatePresence>
        {!isOpen && <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />}
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
              <LanguageToggle onChange={handleLanguageChange} />
              <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-xl transition-colors">
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
                  className={cn('max-w-[85%]', message.role === 'user' ? 'ml-auto' : 'mr-auto')}
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
                    {message.content_ur && language === 'ur' && (
                      <p className="text-sm whitespace-pre-line mt-2 pt-2 border-t border-gray-200/30 dark:border-gray-600/30" dir="rtl">
                        {message.content_ur}
                      </p>
                    )}
                  </div>
                  {message.actions && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {message.actions.map((action, idx) => (
                        <button
                          key={idx}
                          onClick={() => (window.location.href = action.action)}
                          className="text-xs px-3 py-1.5 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}

              {isTyping && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-2 text-gray-500">
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
                    {action.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Voice transcript preview */}
            {voiceTranscript && (
              <div className="px-4 py-2 bg-amber-50 dark:bg-amber-950/20 border-t border-amber-200 dark:border-amber-800">
                <p className="text-xs text-amber-700 dark:text-amber-300">
                  Heard: &quot;{voiceTranscript}&quot;
                  <button onClick={() => handleSend(voiceTranscript, 'voice')} className="ml-2 underline">Send</button>
                  <button onClick={() => { setVoiceTranscript(''); setInputValue(''); }} className="ml-2 underline">Clear</button>
                </p>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex gap-2">
                <VoiceButton onTranscript={handleVoiceTranscript} language={language} disabled={isTyping} />
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder={language === 'ur' ? 'اپنا سوال لکھیں...' : 'Ask me anything...'}
                  dir={language === 'ur' ? 'rtl' : 'ltr'}
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
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
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
