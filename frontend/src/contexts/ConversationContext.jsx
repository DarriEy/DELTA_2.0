import React, { createContext, useContext, useState, useCallback } from 'react';
import { apiClient } from '../api/client';

const ConversationContext = createContext();

export const ConversationProvider = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [activeMode, setActiveMode] = useState('general');
  const [isLoading, setIsLoading] = useState(false);

  const createNewConversation = useCallback(async (mode, userId = 1) => {
    setIsLoading(true);
    try {
      const data = await apiClient.post('/conversations/', { active_mode: mode, user_id: userId });
      setCurrentConversationId(data.conversation_id);
      setConversationHistory([]);
      setActiveMode(mode);
      return data.conversation_id;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((role, content) => {
    setConversationHistory(prev => [...prev, { role, content }]);
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!currentConversationId) {
        console.error("No conversation ID");
        return null;
    }
    
    setIsLoading(true);
    addMessage('user', text);
    
    try {
      let fullResponse = '';
      // Create a placeholder for the assistant's message in the UI
      setConversationHistory(prev => [...prev, { role: 'assistant', content: '' }]);
      
      await apiClient.stream('/api/process_stream', { 
        user_input: text, 
        conversation_id: currentConversationId 
      }, (chunk) => {
        fullResponse += chunk;
        setConversationHistory(prev => {
          const newHistory = [...prev];
          newHistory[newHistory.length - 1].content = fullResponse;
          return newHistory;
        });
      });
      
      return fullResponse;
    } catch (error) {
      console.error('Failed to send streaming message:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, currentConversationId]);

  const value = {
    currentConversationId,
    conversationHistory,
    activeMode,
    isLoading,
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

export const useConversation = () => {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
};
