import React, { useEffect, useRef, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';
import { useSpeech } from '../contexts/SpeechContext';

const ChatMessage = memo(({ msg }) => (
  <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
    <div className={`max-w-[90%] text-sm leading-relaxed
      ${msg.role === 'user' ? 'text-blue-400/80 font-medium' : 'text-white/70'}`}
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
    <div className="flex flex-col h-[450px] relative overflow-hidden bg-white/[0.02] border border-white/[0.05] rounded-3xl shadow-2xl">
      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-10 space-y-8 scrollbar-hide"
      >
        {conversationHistory.length === 0 ? (
          <div className="h-full flex items-center justify-center text-white/10 uppercase tracking-[0.4em] text-[10px] font-bold">
            Ready for input
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <ChatMessage key={idx} msg={msg} />
          ))
        )}
      </div>

      {/* Subtle Listen Indicator */}
      <div className={`absolute bottom-6 right-10 flex items-center gap-2 transition-all duration-500 ${isListening ? 'opacity-100' : 'opacity-0'}`}>
        <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></div>
        <span className="text-[8px] font-black text-red-500 uppercase tracking-[0.4em]">Listening</span>
      </div>
    </div>
  );
};

export default ChatPanel;

export default ChatPanel;
