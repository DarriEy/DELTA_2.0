import { useState, useCallback } from 'react';
import { apiClient } from '../api/client';

export const useConversation = (initialMode = 'general') => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const createNewConversation = useCallback(async (mode, userId = 1) => {
    setIsLoading(true);
    try {
      const data = await apiClient.post('/conversations/', { active_mode: mode, user_id: userId });
      setCurrentConversationId(data.conversation_id);
      setConversationHistory([]);
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

  const sendMessage = useCallback(async (text, mode) => {
    setIsLoading(true);
    try {
      // In AnimatedAvatar, it seems /api/learn was used for simplicity in some places
      // but /api/process is the one that manages history in the backend.
      // For now, let's keep the logic similar to what was there.
      const endpoint = mode === 'educational' ? '/learn' : '/learn';
      const data = await apiClient.post(endpoint, { user_input: text });
      const llmResponse = data.response || data.llmResponse;
      
      if (llmResponse) {
        addMessage('assistant', llmResponse);
        return llmResponse;
      }
      return null;
    } catch (error) {
      console.error('Failed to send message:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  return {
    currentConversationId,
    conversationHistory,
    isLoading,
    createNewConversation,
    addMessage,
    sendMessage,
    setConversationHistory
  };
};
