'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface VoiceButtonProps {
  onTranscript: (text: string, confidence: number) => void;
  language?: string;
  className?: string;
  disabled?: boolean;
}

type SpeechRecognitionType = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
};

export function VoiceButton({ onTranscript, language = 'en', className, disabled }: VoiceButtonProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionType | null>(null);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);
  }, []);

  const startRecording = useCallback(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition: SpeechRecognitionType = new SpeechRecognition();
    recognition.lang = language === 'ur' ? 'ur-PK' : 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = (event: any) => {
      const result = event.results[0][0];
      onTranscript(result.transcript, result.confidence);
      setIsRecording(false);
    };

    recognition.onerror = () => {
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  }, [language, onTranscript]);

  const stopRecording = useCallback(() => {
    recognitionRef.current?.stop();
    setIsRecording(false);
  }, []);

  if (!isSupported) return null;

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled}
      className={cn(
        'p-2.5 rounded-xl transition-all',
        isRecording
          ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-500/30'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-purple-100 dark:hover:bg-purple-900/30 hover:text-purple-600',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      title={isRecording ? 'Stop recording' : 'Start voice input'}
    >
      {isRecording ? (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4M12 15a3 3 0 003-3V5a3 3 0 00-6 0v7a3 3 0 003 3z"
          />
        </svg>
      )}
    </button>
  );
}
