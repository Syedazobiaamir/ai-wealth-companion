'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { apiClient } from '@/lib/api-client';

interface LanguageToggleProps {
  onChange?: (lang: string) => void;
  className?: string;
}

export function LanguageToggle({ onChange, className }: LanguageToggleProps) {
  const [language, setLanguage] = useState<'en' | 'ur'>('en');

  useEffect(() => {
    const saved = localStorage.getItem('ai_language') as 'en' | 'ur' | null;
    if (saved) setLanguage(saved);
  }, []);

  const toggle = async () => {
    const next = language === 'en' ? 'ur' : 'en';
    setLanguage(next);
    localStorage.setItem('ai_language', next);
    onChange?.(next);
    // Persist to backend
    try {
      await apiClient.post('/ai/language', { language: next });
    } catch {
      // Silently fail - localStorage still works as fallback
    }
  };

  return (
    <button
      onClick={toggle}
      className={cn(
        'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium',
        'bg-white/20 hover:bg-white/30 transition-colors',
        'text-white',
        className
      )}
      title={language === 'en' ? 'Switch to Urdu' : 'Switch to English'}
    >
      <span className={cn(language === 'en' ? 'font-bold' : 'opacity-60')}>EN</span>
      <span className="opacity-40">/</span>
      <span className={cn(language === 'ur' ? 'font-bold' : 'opacity-60')}>اردو</span>
    </button>
  );
}
