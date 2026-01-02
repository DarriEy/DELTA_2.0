import React, { useEffect, useRef, memo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';
import { useSpeech } from '../contexts/SpeechContext';

const ChatMessage = memo(({ msg }) => (
  <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-2 group`}>
    <span className={`text-[8px] uppercase tracking-[0.3em] font-black opacity-30 group-hover:opacity-60 transition-opacity ${msg.role === 'user' ? 'mr-2' : 'ml-2'}`}>
      {msg.role === 'user' ? 'Commander' : 'Delta Core'}
    </span>
    <div className={`max-w-[85%] text-sm leading-relaxed p-4 rounded-2xl transition-all duration-500
      ${msg.role === 'user' 
        ? 'bg-blue-500/10 border border-blue-500/20 text-blue-100 rounded-tr-none shadow-[0_0_20px_rgba(59,130,246,0.1)]' 
        : 'bg-white/5 border border-white/10 text-white/90 rounded-tl-none hover:bg-white/10'}`}
    >
      <ReactMarkdown 
        remarkPlugins={[remarkMath]} 
        rehypePlugins={[rehypeKatex]}
        className="markdown-content"
      >
        {msg.content}
      </ReactMarkdown>
    </div>
  </div>
));

const ChatPanel = ({ isActive, setIsProcessing }) => {
  const { conversationHistory, sendMessage, isLoading } = useConversation();
  const { isListening } = useSpeech();
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
    <div className={`flex flex-col h-[450px] relative overflow-hidden transition-all duration-1000 border rounded-[2rem] shadow-2xl
      ${isActive 
        ? 'bg-black/40 backdrop-blur-2xl border-white/10 opacity-100 translate-y-0 scale-100' 
        : 'bg-transparent border-transparent opacity-40 translate-y-4 scale-[0.98] grayscale blur-[2px]'}`}
    >
      {/* HUD Header Decoration */}
      <div className="flex items-center justify-between px-8 py-4 border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse shadow-[0_0_8px_#3b82f6]"></div>
          <span className="text-[9px] font-black uppercase tracking-[0.5em] text-white/40">Secure Stream</span>
        </div>
        <div className="flex gap-1">
          {[1, 2, 3].map(i => (
            <div key={i} className="w-8 h-[1px] bg-white/10"></div>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className={`flex-1 overflow-y-auto p-8 space-y-10 scrollbar-hide pb-24 ${isActive ? 'pointer-events-auto' : 'pointer-events-none'}`}
      >
        {conversationHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center space-y-4">
            <div className="w-12 h-[1px] bg-white/10 animate-pulse"></div>
            <span className="text-white/5 uppercase tracking-[0.6em] text-[10px] font-bold">Initialize Avatar to Begin</span>
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <ChatMessage key={idx} msg={msg} />
          ))
        )}
      </div>

      {/* Input Area */}
      <div className={`absolute bottom-0 left-0 right-0 p-6 transition-all duration-700 delay-300 z-50
        ${isActive ? 'opacity-100 translate-y-0 pointer-events-auto' : 'opacity-0 translate-y-10 pointer-events-none'}`}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent pointer-events-none"></div>
        <form onSubmit={handleSubmit} className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500 pointer-events-none"></div>
          <div className="relative flex items-center gap-2 bg-white/[0.03] border border-white/10 rounded-2xl p-1.5 focus-within:border-blue-500/40 transition-all">
            <input
              type="text"
              autoFocus
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={isListening ? "Syncing voice stream..." : "Input command sequence..."}
              className="flex-1 bg-transparent px-4 py-2 text-sm focus:outline-none placeholder:text-white/10 text-white font-light tracking-wide disabled:opacity-50"
              disabled={isLoading || !isActive}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || isLoading || !isActive}
              className={`p-3 rounded-xl transition-all duration-500
                ${inputText.trim() && !isLoading 
                  ? 'text-blue-400 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.2)]' 
                  : 'text-white/5 bg-transparent'}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
              </svg>
            </button>
          </div>
        </form>
      </div>

      {/* Mic Active Decor */}
      <div className={`absolute top-12 right-8 flex flex-col items-end gap-1 transition-all duration-500 ${isListening ? 'opacity-100' : 'opacity-0 scale-90 translate-x-4'}`}>
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></div>
          <span className="text-[7px] font-black text-red-500 uppercase tracking-[0.4em]">Mic Active</span>
        </div>
        <div className="w-24 h-[1px] bg-gradient-to-l from-red-500/50 to-transparent"></div>
      </div>
    </div>
  );
};

export default ChatPanel;
