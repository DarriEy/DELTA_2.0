import React, { useEffect, useRef, memo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';

const ChatMessage = memo(({ msg }) => (
  <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-2 group animate-in fade-in slide-in-from-bottom-2 duration-500`}>
    <div className={`flex items-center gap-3 mb-1 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-1.5 h-1.5 rounded-full ${msg.role === 'user' ? 'bg-blue-500/50' : 'bg-slate-400/50'}`}></div>
      <span className="text-[10px] uppercase tracking-[0.25em] font-semibold text-slate-500">
        {msg.role === 'user' ? 'System Inquiry' : 'Unit Analysis'}
      </span>
    </div>
    
    <div className={`max-w-[95%] text-sm leading-relaxed px-6 py-5 rounded-2xl border transition-all duration-500
      ${msg.role === 'user' 
        ? 'bg-slate-800/30 border-slate-700/50 text-slate-200 rounded-tr-none shadow-lg shadow-blue-900/5' 
        : 'bg-slate-900/40 border-slate-800/80 text-slate-300 rounded-tl-none shadow-xl'}`}
    >
      <ReactMarkdown 
        remarkPlugins={[remarkMath]} 
        rehypePlugins={[rehypeKatex]}
        className="markdown-content font-light tracking-wide selection:bg-slate-700"
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
    <div className={`flex flex-col h-[520px] relative overflow-hidden transition-all duration-700 rounded-3xl border
      ${isActive 
        ? 'bg-slate-950/40 border-slate-800/60 opacity-100 shadow-2xl' 
        : 'bg-transparent border-transparent opacity-10 grayscale pointer-events-none'}`}
    >
      {/* Interface Header */}
      <div className="px-8 py-4 border-b border-slate-800/40 bg-slate-900/20 backdrop-blur-sm flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500/20"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500/20"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/20"></div>
          </div>
          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-[0.3em]">Neural Stream v2.0</span>
        </div>
        {isLoading && (
          <div className="flex items-center gap-2">
            <span className="text-[8px] text-slate-500 uppercase tracking-widest animate-pulse">Processing</span>
            <div className="w-8 h-[1px] bg-slate-800 overflow-hidden">
              <div className="w-full h-full bg-slate-400 animate-progress-slide"></div>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className={`flex-1 overflow-y-auto p-8 space-y-10 scroll-smooth scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent pb-32
          ${isActive ? 'pointer-events-auto' : 'pointer-events-none'}`}
      >
        {conversationHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center space-y-4 opacity-30">
            <div className="w-12 h-12 rounded-full border border-dashed border-slate-700 flex items-center justify-center">
              <span className="text-xl">⌬</span>
            </div>
            <span className="text-slate-400 uppercase tracking-[0.5em] text-[10px] font-medium">System Idle</span>
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <ChatMessage key={idx} msg={msg} />
          ))
        )}
      </div>

      {/* Input Area */}
      <div className={`absolute bottom-0 left-0 right-0 p-6 transition-all duration-700
        ${isActive ? 'opacity-100' : 'opacity-0 translate-y-4'}`}
      >
        <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-md border-t border-slate-800/50 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]"></div>
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-center gap-6 bg-slate-900/50 border border-slate-800/50 rounded-xl px-6 py-1 focus-within:border-slate-700 transition-colors">
            <input
              type="text"
              autoFocus
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Send instruction..."
              className="flex-1 bg-transparent py-3 text-sm focus:outline-none placeholder:text-slate-700 text-slate-200 font-light tracking-wider"
              disabled={isLoading || !isActive}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || isLoading || !isActive}
              className={`flex items-center gap-3 text-[9px] font-bold uppercase tracking-[0.3em] transition-all duration-300
                ${inputText.trim() && !isLoading 
                  ? 'text-white opacity-100 hover:text-blue-400' 
                  : 'text-slate-700 opacity-50'}`}
            >
              <span>Execute</span>
              <span className="text-lg opacity-50">↵</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPanel;