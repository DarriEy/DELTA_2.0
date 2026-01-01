import React, { createContext, useContext, useState, useCallback, useReducer } from 'react';
import { apiClient } from '../api/client';
import { conversationReducer } from './conversationReducer';

const ConversationContext = createContext();

export const ConversationProvider = ({ children }) => {
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationHistory, dispatch] = useReducer(conversationReducer, []);
  const [activeMode, setActiveMode] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createNewConversation = useCallback(async (mode, userId = 101) => {
    setIsLoading(true);
    setError(null);
    console.log("DELTA: Creating conversation for mode:", mode);
    try {
      const data = await apiClient.post('/conversations/', { active_mode: mode, user_id: userId });
      console.log("DELTA: Conversation established:", data.id);
      setCurrentConversationId(data.id);
      dispatch({ type: "reset" });
      setActiveMode(mode);
      return data.id;
    } catch (error) {
      console.error('DELTA: Failed to create conversation:', error);
      setError('Connection failed. Please check your network.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((role, content) => {
    dispatch({ type: "add", message: { role, content } });
  }, []);

  const setConversationHistory = useCallback((history) => {
    dispatch({ type: "replace", history });
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
      dispatch({ type: "start_assistant_message" });

      const updateMessage = (newContent) => {
        dispatch({ type: "update_last_assistant", content: newContent });
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
