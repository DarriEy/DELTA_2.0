import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useConversation } from '../contexts/ConversationContext';
import { useSpeech } from '../contexts/SpeechContext';

const ChatPanel = () => {
  const { conversationHistory } = useConversation();
  const { isListening } = useSpeech();

  return (
    <div className="glass-card p-6 h-[400px] flex flex-col relative overflow-hidden group">
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/10">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <span className="text-blue-400">💬</span> Conversation
        </h3>
        <div className="flex gap-2">
           <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
           <span className="text-[10px] text-white/40 uppercase tracking-widest">Live Stream</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin">
        {conversationHistory.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-white/30 text-center px-8">
            <p className="text-lg font-light mb-2 italic">"How should we save the world today?"</p>
            <p className="text-xs uppercase tracking-widest">Click Delta to start</p>
          </div>
        ) : (
          conversationHistory.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-lg
                ${msg.role === 'user' 
                  ? 'bg-blue-600/30 border border-blue-400/30 rounded-tr-none' 
                  : 'bg-white/10 border border-white/10 backdrop-blur-md rounded-tl-none'}`}
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
          ))
        )}
      </div>

      <div className={`absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-black/40 backdrop-blur-xl border border-white/10 rounded-full text-[10px] uppercase tracking-widest transition-opacity duration-300 ${isListening ? 'opacity-100' : 'opacity-0'}`}>
        Delta is listening...
      </div>
    </div>
  );
};

export default ChatPanel;
