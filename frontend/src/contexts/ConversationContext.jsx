import React, { createContext, useContext, useState, useCallback } from 'react';
import { apiClient } from '../api/client';

const ConversationContext = createContext();

export const ConversationProvider = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [activeMode, setActiveMode] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createNewConversation = useCallback(async (mode, userId = 101) => {
    setIsLoading(true);
    setError(null);
    console.log("DELTA: Creating conversation for mode:", mode);
    try {
      const data = await apiClient.post('/conversations/', { active_mode: mode, user_id: userId });
      console.log("DELTA: Conversation established:", data.conversation_id);
      setCurrentConversationId(data.conversation_id);
      setConversationHistory([]);
      setActiveMode(mode);
      return data.conversation_id;
    } catch (error) {
      console.error('DELTA: Failed to create conversation:', error);
      setError('Connection failed. Please check your network.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((role, content) => {
    setConversationHistory(prev => [...prev, { role, content }]);
  }, []);

  const sendMessage = useCallback(async (text, onChunkReceived) => { // Changed back to async function, added onChunkReceived
    let conversationId = currentConversationId;
    if (!conversationId) {
        console.log("DELTA: No conversation ID found, creating one...");
        conversationId = await createNewConversation(activeMode);
        if (!conversationId) {
            console.error("DELTA: Failed to create conversation on the fly.");
            return; // Use return for async function
        }
    }
    
    setIsLoading(true);
    addMessage('user', text);
    
    try {
      let fullResponse = '';
      // Create a placeholder for the assistant's message in the UI
      setConversationHistory(prev => [...prev.filter(msg => msg.content !== ''), { role: 'assistant', content: '' }]);
      
      const updateMessage = (newContent) => {
        setConversationHistory(prev => {
          const newHistory = [...prev];
          const lastAssistantMessageIndex = newHistory.findLastIndex(msg => msg.role === 'assistant');
          if (lastAssistantMessageIndex !== -1) {
            newHistory[lastAssistantMessageIndex].content = newContent;
          }
          return newHistory;
        });
      };

      await apiClient.stream('/process_stream', { 
        user_input: text, 
        conversation_id: conversationId 
      }, (chunk) => {
        fullResponse += chunk;
        updateMessage(fullResponse);
        if (onChunkReceived) {
          onChunkReceived(chunk); // Call the callback with the chunk
        }
      });
      
      return fullResponse; // Return the full response after stream ends
      
    } catch (error) {
      console.error('Failed to send streaming message:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, currentConversationId, createNewConversation, activeMode]);

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
