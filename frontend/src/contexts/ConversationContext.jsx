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

  const sendMessage = useCallback(async function* (text) { // Changed to async generator
    let conversationId = currentConversationId;
    if (!conversationId) {
        console.log("DELTA: No conversation ID found, creating one...");
        conversationId = await createNewConversation(activeMode);
        if (!conversationId) {
            console.error("DELTA: Failed to create conversation on the fly.");
            return; // Use return for generator to stop
        }
    }
    
    setIsLoading(true);
    addMessage('user', text);
    
    try {
      let fullResponse = '';
      // Create a placeholder for the assistant's message in the UI
      setConversationHistory(prev => [...prev.filter(msg => msg.content !== ''), { role: 'assistant', content: '' }]); // Filter out potential empty messages
      
      const updateMessage = (newContent) => {
        setConversationHistory(prev => {
          const newHistory = [...prev];
          // Ensure we update the last assistant message
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
        // Yield each chunk as it comes in
        // console.log("sendMessage yield chunk:", chunk); // For debugging
        // Use yield* to delegate to another async generator if needed, or simply yield chunk
        // For now, yield the current full response to track progress, but the caller will decide what to speak
        // For actual streaming speech, we need to yield smaller, actionable chunks or process sentence boundaries here.
        // For now, let's yield the chunk and let AnimatedAvatar decide when to speak.
        yield chunk; // Yield the chunk directly
      });
      
      // After the stream ends, ensure any remaining content is yielded
      // The last updateMessage already handled the fullResponse.
      
    } catch (error) {
      console.error('Failed to send streaming message:', error);
      // It's good practice for generators to re-raise or yield an error state if they fail
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
