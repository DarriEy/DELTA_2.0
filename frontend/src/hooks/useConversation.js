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
    // Add user message to history immediately for UI responsiveness
    addMessage('user', text);
    
    try {
      // Use /process if we have a conversation_id, otherwise fall back to /learn
      const endpoint = currentConversationId ? '/process' : '/learn';
      const payload = currentConversationId 
        ? { user_input: text, conversation_id: currentConversationId }
        : { user_input: text };

      const data = await apiClient.post(endpoint, payload);
      const llmResponse = data.llmResponse || data.response;
      
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
  }, [addMessage, currentConversationId]);

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
