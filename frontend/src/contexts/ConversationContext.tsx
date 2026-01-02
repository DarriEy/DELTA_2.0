import React, { createContext, useContext, useState, useCallback, useReducer, ReactNode } from 'react';
import { apiClient } from '../api/client';
import { conversationReducer } from './conversationReducer';
import type { Message, ConversationAction } from './conversationReducer';

interface Conversation {
  id: number;
  active_mode: string;
  user_id?: number;
  start_time: string;
  summary?: string;
}

interface ConversationContextType {
  currentConversationId: number | null;
  conversationHistory: Message[];
  activeMode: string;
  isLoading: boolean;
  error: string | null;
  setActiveMode: (mode: string) => void;
  createNewConversation: (mode: string, userId?: number) => Promise<number | null>;
  addMessage: (role: 'user' | 'assistant' | 'model', content: string) => void;
  addLocalAssistantMessage: (content: string) => void;
  sendMessage: (text: string, onChunkReceived?: (chunk: string) => void) => Promise<string | undefined>;
  setConversationHistory: (history: Message[]) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  console.log("DELTA: ConversationProvider rendering");
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(999);
  const [conversationHistory, dispatch] = useReducer(conversationReducer, []);
  const [activeMode, setActiveMode] = useState<string>('general');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const createNewConversation = useCallback(async (mode: string, userId = 101): Promise<number | null> => {
    setIsLoading(true);
    setError(null);
    console.log("DELTA: Creating stateless session for mode:", mode);
    try {
      // Mock conversation establishment
      setCurrentConversationId(999);
      dispatch({ type: "reset" });
      setActiveMode(mode);
      return 999;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((role: 'user' | 'assistant' | 'model', content: string) => {
    dispatch({ type: "add", message: { role, content } });
  }, []);

  const addLocalAssistantMessage = useCallback((content: string) => {
    dispatch({ type: "add", message: { role: 'assistant', content } });
  }, []);

  const setConversationHistory = useCallback((history: Message[]) => {
    dispatch({ type: "replace", history });
  }, []);

  const sendMessage = useCallback(async (text: string, onChunkReceived?: (chunk: string) => void): Promise<string | undefined> => {
    setIsLoading(true);
    addMessage('user', text);
    
    try {
      let fullResponse = '';
      dispatch({ type: "start_assistant_message" });

      const updateMessage = (newContent: string) => {
        dispatch({ type: "update_last_assistant", content: newContent });
      };

      await apiClient.stream('/process_stream', { 
        user_input: text, 
        conversation_id: 999 
      }, (chunk: string) => {
        fullResponse += chunk;
        updateMessage(fullResponse);
        if (onChunkReceived) {
          onChunkReceived(chunk);
        }
      });
      
      return fullResponse;
      
    } catch (err: any) {
      console.error('Failed to send streaming message:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const value: ConversationContextType = {
    currentConversationId,
    conversationHistory,
    activeMode,
    isLoading,
    error,
    setActiveMode,
    createNewConversation,
    addMessage,
    addLocalAssistantMessage,
    sendMessage,
    setConversationHistory
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
};

export const useConversation = (): ConversationContextType => {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
};