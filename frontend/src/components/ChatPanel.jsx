import React, { useEffect, useRef, memo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';

const ChatMessage = memo(({ msg }) => (
  <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-3 group`}>
    <span className={`text-[9px] uppercase tracking-[0.2em] font-medium opacity-40 ${msg.role === 'user' ? 'mr-1' : 'ml-1'}`}>
      {msg.role === 'user' ? 'Inquiry' : 'Analysis'}
    </span>
    <div className={`max-w-[90%] text-sm leading-relaxed p-5 border transition-all duration-300
      ${msg.role === 'user' 
        ? 'bg-slate-800/20 border-slate-700 text-slate-200' 
        : 'bg-transparent border-slate-800/50 text-slate-300'}`}
    >
      <ReactMarkdown 
        remarkPlugins={[remarkMath]} 
        rehypePlugins={[rehypeKatex]}
        className="markdown-content font-light tracking-wide"
      >
        {msg.content}
      </ReactMarkdown>
    </div>
  </div>
));

const ChatPanel = ({ isActive, setIsProcessing }) => {
  const { conversationHistory, sendMessage, isLoading } = useConversation();
  const [inputText, setInputText] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [conversationHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const text = inputText;
    setInputText('');
    
    try {
      if (setIsProcessing) setIsProcessing(true);
      await sendMessage(text);
    } catch (err) {
      console.error("Failed to send message:", err);
    } finally {
      if (setIsProcessing) setIsProcessing(false);
    }
  };

  return (
    <div className={`flex flex-col h-[500px] relative overflow-hidden transition-all duration-1000 border-l border-r
      ${isActive 
        ? 'bg-slate-950/20 border-slate-800 opacity-100' 
        : 'bg-transparent border-transparent opacity-20 grayscale pointer-events-none'}`}
    >
      {/* Messages */}
      <div 
        ref={scrollRef}
        className={`flex-1 overflow-y-auto p-10 space-y-12 scrollbar-hide pb-32 ${isActive ? 'pointer-events-auto' : 'pointer-events-none'}`}
      >
        {conversationHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center space-y-6 opacity-20">
            <span className="text-slate-400 uppercase tracking-[0.4em] text-[10px] font-medium">Research Interface Standby</span>
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <ChatMessage key={idx} msg={msg} />
          ))
        )}
      </div>

      {/* Input Area */}
      <div className={`absolute bottom-0 left-0 right-0 p-8 transition-all duration-700
        ${isActive ? 'opacity-100' : 'opacity-0 translate-y-4'}`}
      >
        <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm border-t border-slate-800"></div>
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-center gap-4">
            <input
              type="text"
              autoFocus
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Submit inquiry..."
              className="flex-1 bg-transparent py-2 text-sm focus:outline-none placeholder:text-slate-700 text-slate-200 font-light tracking-widest"
              disabled={isLoading || !isActive}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || isLoading || !isActive}
              className={`text-[10px] font-bold uppercase tracking-[0.2em] transition-all duration-300
                ${inputText.trim() && !isLoading 
                  ? 'text-slate-200 opacity-100 hover:tracking-[0.3em]' 
                  : 'text-slate-700 opacity-50'}`}
            >
              Execute
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;