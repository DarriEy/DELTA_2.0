import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';
import { useSpeech } from '../contexts/SpeechContext';

const ChatPanel = () => {
  const { conversationHistory } = useConversation();
  const { isListening } = useSpeech();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [conversationHistory]);

  return (
    <div className="glass-card flex flex-col h-[500px] relative overflow-hidden bg-slate-900/40 backdrop-blur-3xl border border-white/10 rounded-[2rem] shadow-2xl">
      {/* Panel Header */}
      <div className="flex items-center justify-between px-8 py-6 border-b border-white/5 bg-white/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400 border border-blue-500/20">
            💬
          </div>
          <div>
            <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-white/90">Communication</h3>
            <p className="text-[10px] text-white/30 uppercase tracking-widest">Neural Stream Active</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full">
           <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
           <span className="text-[9px] font-bold text-green-400 uppercase tracking-widest">Live</span>
        </div>
      </div>

      {/* Messages Stream */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-hide scroll-smooth"
      >
        {conversationHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-12 space-y-4 opacity-40">
            <div className="w-16 h-16 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-3xl">
              🌊
            </div>
            <div>
              <p className="text-lg font-light italic mb-1">"Awaiting hydrological inquiries..."</p>
              <p className="text-[10px] uppercase tracking-[0.2em]">Initiate sequence via Delta</p>
            </div>
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
              <div className={`max-w-[85%] p-5 rounded-3xl text-sm leading-relaxed shadow-xl border
                ${msg.role === 'user' 
                  ? 'bg-blue-600/20 border-blue-500/30 text-blue-50 rounded-tr-none' 
                  : 'bg-white/5 border-white/10 text-white/90 backdrop-blur-md rounded-tl-none'}`}
              >
                <div className="flex items-center gap-2 mb-2 opacity-30">
                   <span className="text-[9px] font-bold uppercase tracking-widest">{msg.role}</span>
                   <div className="h-[1px] flex-1 bg-current opacity-20"></div>
                </div>
                <ReactMarkdown 
                  remarkPlugins={[remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                  className="markdown-content prose prose-invert prose-sm max-w-none"
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input Overlay */}
      <div className={`absolute bottom-6 left-1/2 -translate-x-1/2 px-6 py-2.5 bg-red-500/20 backdrop-blur-2xl border border-red-500/30 rounded-full text-[10px] font-bold text-red-400 uppercase tracking-[0.3em] transition-all duration-500 shadow-lg shadow-red-900/20 ${isListening ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95 pointer-events-none'}`}>
        Delta Listening
      </div>
    </div>
  );
};

export default ChatPanel;