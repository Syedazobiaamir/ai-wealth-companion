'use client';

/**
 * ChatKit Wrapper Component
 *
 * Integrates OpenAI ChatKit SDK with the AI Wealth Companion.
 * Falls back to custom chat widget if ChatKit is not available.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { aiApi } from '@/lib/api';
import { LanguageToggle } from '@/components/ai/language-toggle';
import { VoiceButton } from '@/components/ai/voice-button';
import {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  WELCOME_MESSAGES,
  PLACEHOLDERS,
  SUGGESTED_PROMPTS,
  sendChatMessage,
  formatToolCallResult,
} from '@/lib/chatkit-config';

interface ChatKitWrapperProps {
  className?: string;
  initialOpen?: boolean;
  position?: 'bottom-right' | 'bottom-left' | 'embedded';
  onMessageSent?: (message: string) => void;
  onResponseReceived?: (response: ChatResponse) => void;
}

export function ChatKitWrapper({
  className,
  initialOpen = false,
  position = 'bottom-right',
  onMessageSent,
  onResponseReceived,
}: ChatKitWrapperProps) {
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [language, setLanguage] = useState<'en' | 'ur'>('en');
  const [voiceTranscript, setVoiceTranscript] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load saved language preference
  useEffect(() => {
    const saved = localStorage.getItem('ai_language');
    if (saved === 'en' || saved === 'ur') {
      setLanguage(saved);
    }
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: WELCOME_MESSAGES[language],
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [language, messages.length]);

  // Scroll to bottom on new messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle sending a message
  const handleSend = async (query?: string, inputMethod: 'text' | 'voice' = 'text') => {
    const messageText = query || inputValue;
    if (!messageText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      input_method: inputMethod,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setVoiceTranscript('');
    setIsTyping(true);

    onMessageSent?.(messageText);

    try {
      // Use the chat API
      const response = await aiApi.chat(
        messageText,
        conversationId,
        language,
        inputMethod
      );

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const aiMessage: ChatMessage = {
        id: response.message_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response || 'I could not process that request.',
        content_ur: response.response_ur,
        timestamp: new Date().toISOString(),
        intent: response.intent,
        confidence: response.confidence,
        tool_calls: response.tool_calls,
      };

      setMessages((prev) => [...prev, aiMessage]);
      onResponseReceived?.(response);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: language === 'ur'
          ? 'معذرت، کچھ مسئلہ ہوا۔ براہ کرم دوبارہ کوشش کریں۔'
          : "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Handle voice transcript
  const handleVoiceTranscript = useCallback(
    (text: string, confidence: number) => {
      if (confidence >= 0.7) {
        handleSend(text, 'voice');
      } else {
        setVoiceTranscript(text);
        setInputValue(text);
      }
    },
    [conversationId, language]
  );

  // Handle language change
  const handleLanguageChange = (lang: string) => {
    const newLang = lang as 'en' | 'ur';
    setLanguage(newLang);
    // Update welcome message when language changes
    if (messages.length === 1 && messages[0].id === 'welcome') {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: WELCOME_MESSAGES[newLang],
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  // Position classes
  const positionClasses = {
    'bottom-right': 'fixed bottom-40 right-6 lg:bottom-24',
    'bottom-left': 'fixed bottom-40 left-6 lg:bottom-24',
    embedded: 'relative',
  };

  const buttonPositionClasses = {
    'bottom-right': 'fixed bottom-24 right-6 lg:bottom-6',
    'bottom-left': 'fixed bottom-24 left-6 lg:bottom-6',
    embedded: 'hidden',
  };

  return (
    <>
      {/* Chat Button (hidden if embedded) */}
      {position !== 'embedded' && (
        <motion.button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            buttonPositionClasses[position],
            'z-50 w-14 h-14 rounded-full',
            'bg-gradient-to-r from-purple-600 to-blue-500 text-white',
            'flex items-center justify-center',
            'shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50',
            'transition-shadow'
          )}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}
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
          {!isOpen && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />
          )}
        </motion.button>
      )}

      {/* Chat Window */}
      <AnimatePresence>
        {(isOpen || position === 'embedded') && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={cn(
              positionClasses[position],
              'z-50',
              position === 'embedded' ? 'w-full h-full' : 'w-80 sm:w-96 h-[32rem]',
              'bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl',
              'rounded-3xl shadow-2xl shadow-purple-500/20',
              'border border-white/30 dark:border-gray-700/50',
              'flex flex-col overflow-hidden',
              className
            )}
          >
            {/* Header */}
            <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-600 to-blue-500 text-white">
              <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">AI Wealth Companion</h3>
                <p className="text-xs text-white/80 flex items-center gap-1">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  {language === 'ur' ? 'آن لائن' : 'Online'}
                </p>
              </div>
              <LanguageToggle onChange={handleLanguageChange} />
              {position !== 'embedded' && (
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/10 rounded-xl transition-colors"
                  aria-label="Close chat"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
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
                      <p
                        className="text-sm whitespace-pre-line mt-2 pt-2 border-t border-gray-200/30 dark:border-gray-600/30"
                        dir="rtl"
                      >
                        {message.content_ur}
                      </p>
                    )}
                    {/* Show tool calls if any */}
                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200/30 dark:border-gray-600/30">
                        {message.tool_calls.map((tc, idx) => (
                          <p key={idx} className="text-xs text-gray-500 dark:text-gray-400">
                            {formatToolCallResult(tc)}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                  {/* Confidence indicator for AI messages */}
                  {message.role === 'assistant' && message.confidence && (
                    <p className="text-xs text-gray-400 mt-1">
                      {message.intent} ({Math.round(message.confidence * 100)}%)
                    </p>
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

            {/* Suggested Prompts */}
            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {SUGGESTED_PROMPTS[language].map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    className="flex-shrink-0 text-xs px-3 py-1.5 rounded-full bg-gray-100 dark:bg-gray-800 text-slate-700 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 hover:text-purple-700 dark:hover:text-purple-300 transition-colors duration-200 whitespace-nowrap cursor-pointer"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Voice transcript preview */}
            {voiceTranscript && (
              <div className="px-4 py-2 bg-amber-50 dark:bg-amber-950/20 border-t border-amber-200 dark:border-amber-800">
                <p className="text-xs text-amber-700 dark:text-amber-300">
                  {language === 'ur' ? 'سنا:' : 'Heard:'} &quot;{voiceTranscript}&quot;
                  <button onClick={() => handleSend(voiceTranscript, 'voice')} className="ml-2 underline">
                    {language === 'ur' ? 'بھیجیں' : 'Send'}
                  </button>
                  <button
                    onClick={() => {
                      setVoiceTranscript('');
                      setInputValue('');
                    }}
                    className="ml-2 underline"
                  >
                    {language === 'ur' ? 'صاف کریں' : 'Clear'}
                  </button>
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
                  placeholder={PLACEHOLDERS[language]}
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
                  aria-label={language === 'ur' ? 'بھیجیں' : 'Send message'}
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

export default ChatKitWrapper;
