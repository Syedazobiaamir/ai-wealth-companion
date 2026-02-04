'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { aiApi } from '@/lib/api';
import { VoiceButton } from '@/components/ai/voice-button';
import { LanguageToggle } from '@/components/ai/language-toggle';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  content_ur?: string;
  timestamp: Date;
  intent?: string;
  confidence?: number;
}

const SUGGESTED_PROMPTS = [
  { icon: '📊', text: 'Show my financial summary', category: 'Overview' },
  { icon: '💰', text: 'How much did I spend this month?', category: 'Spending' },
  { icon: '📈', text: 'Analyze my spending patterns', category: 'Analysis' },
  { icon: '🎯', text: 'How are my budgets doing?', category: 'Budgets' },
  { icon: '💡', text: 'Give me saving tips', category: 'Tips' },
  { icon: '🏦', text: 'Can I invest 50,000 PKR?', category: 'Investment' },
  { icon: '⏰', text: 'Remind me to pay bills tomorrow', category: 'Tasks' },
  { icon: '📋', text: 'Show my pending tasks', category: 'Tasks' },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [language, setLanguage] = useState<string>('en');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('ai_language');
    if (saved) setLanguage(saved);
    inputRef.current?.focus();
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
      setInputValue(text);
    }
  }, [conversationId, language]);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] -mx-4 -my-6">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-white dark:border-gray-900" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI Financial Assistant</h1>
            <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              Online and ready to help
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <LanguageToggle onChange={handleLanguageChange} />
          <button
            onClick={() => {
              setMessages([]);
              setConversationId(undefined);
            }}
            className="p-2 rounded-xl text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            title="New conversation"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full text-center px-4"
          >
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-2xl shadow-purple-500/30 mb-6">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              How can I help you today?
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-md">
              I can help you track expenses, manage budgets, analyze spending patterns, simulate investments, and manage your financial tasks.
            </p>

            {/* Suggested Prompts */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl">
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => handleSend(prompt.text)}
                  className={cn(
                    'flex flex-col items-start gap-2 p-4 rounded-2xl text-left',
                    'bg-white dark:bg-gray-800/50',
                    'border border-gray-200 dark:border-gray-700',
                    'hover:border-purple-300 dark:hover:border-purple-600',
                    'hover:shadow-lg hover:shadow-purple-500/10',
                    'transition-all duration-200'
                  )}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="text-2xl">{prompt.icon}</span>
                  <span className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                    {prompt.text}
                  </span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <>
            {messages.map((message, idx) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={cn(
                  'flex gap-3 max-w-3xl',
                  message.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                )}
              >
                {/* Avatar */}
                <div className={cn(
                  'flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center',
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-purple-600 to-blue-500'
                    : 'bg-gray-100 dark:bg-gray-800'
                )}>
                  {message.role === 'user' ? (
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  )}
                </div>

                {/* Message Bubble */}
                <div className={cn(
                  'flex flex-col gap-1 max-w-[80%]',
                  message.role === 'user' ? 'items-end' : 'items-start'
                )}>
                  <div className={cn(
                    'px-4 py-3 rounded-2xl',
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white rounded-br-md'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-bl-md'
                  )}>
                    <p className="text-sm whitespace-pre-line">{message.content}</p>
                    {message.content_ur && language === 'ur' && (
                      <p className="text-sm whitespace-pre-line mt-3 pt-3 border-t border-white/20 dark:border-gray-600/30" dir="rtl">
                        {message.content_ur}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-gray-400 px-1">
                    {formatTime(message.timestamp)}
                    {message.role === 'assistant' && message.intent && (
                      <span className="ml-2 text-purple-500">({message.intent})</span>
                    )}
                  </span>
                </div>
              </motion.div>
            ))}

            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 max-w-3xl mr-auto"
              >
                <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-3">
            <VoiceButton
              onTranscript={handleVoiceTranscript}
              language={language}
              disabled={isTyping}
            />
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder={language === 'ur' ? 'اپنا سوال لکھیں...' : 'Type your message...'}
                dir={language === 'ur' ? 'rtl' : 'ltr'}
                className={cn(
                  'w-full px-5 py-3.5 rounded-2xl',
                  'bg-gray-100 dark:bg-gray-800',
                  'text-gray-900 dark:text-white',
                  'placeholder:text-gray-500',
                  'focus:outline-none focus:ring-2 focus:ring-purple-500/50',
                  'transition-all'
                )}
              />
            </div>
            <motion.button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isTyping}
              className={cn(
                'p-3.5 rounded-2xl',
                'bg-gradient-to-r from-purple-600 to-blue-500 text-white',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'shadow-lg shadow-purple-500/25',
                'hover:shadow-purple-500/40 transition-shadow'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </motion.button>
          </div>
          <p className="text-xs text-center text-gray-400 mt-3">
            AI Assistant can help with budgets, spending analysis, investments, and task management
          </p>
        </div>
      </div>
    </div>
  );
}
