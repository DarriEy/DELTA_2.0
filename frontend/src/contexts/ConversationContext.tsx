import React, { createContext, useContext, useState, useCallback, useReducer, ReactNode } from 'react';
import { apiClient } from '../api/client';
import { conversationReducer, Message, ConversationAction } from './conversationReducer';

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
  sendMessage: (text: string, onChunkReceived?: (chunk: string) => void) => Promise<string | undefined>;
  setConversationHistory: (history: Message[]) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [conversationHistory, dispatch] = useReducer(conversationReducer, []);
  const [activeMode, setActiveMode] = useState<string>('general');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const createNewConversation = useCallback(async (mode: string, userId = 101): Promise<number | null> => {
    setIsLoading(true);
    setError(null);
    console.log("DELTA: Creating conversation for mode:", mode);
    try {
      const data = await apiClient.post<Conversation>('/conversations/', { active_mode: mode, user_id: userId });
      console.log("DELTA: Conversation established:", data.id);
      setCurrentConversationId(data.id);
      dispatch({ type: "reset" });
      setActiveMode(mode);
      return data.id;
    } catch (err: any) {
      console.error('DELTA: Failed to create conversation:', err);
      setError('Connection failed. Please check your network.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((role: 'user' | 'assistant' | 'model', content: string) => {
    dispatch({ type: "add", message: { role, content } });
  }, []);

  const setConversationHistory = useCallback((history: Message[]) => {
    dispatch({ type: "replace", history });
  }, []);

  const sendMessage = useCallback(async (text: string, onChunkReceived?: (chunk: string) => void): Promise<string | undefined> => {
    let conversationId = currentConversationId;
    if (!conversationId) {
        console.log("DELTA: No conversation ID found, creating one...");
        conversationId = await createNewConversation(activeMode);
        if (!conversationId) {
            console.error("DELTA: Failed to create conversation on the fly.");
            return;
        }
    }
    
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
        conversation_id: conversationId 
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
  }, [addMessage, currentConversationId, createNewConversation, activeMode]);

  const value: ConversationContextType = {
    currentConversationId,
    conversationHistory,
    activeMode,
    isLoading,
    error,
    setActiveMode,
    createNewConversation,
    addMessage,
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