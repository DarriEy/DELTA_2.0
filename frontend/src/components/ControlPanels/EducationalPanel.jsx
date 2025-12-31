import React from 'react';

const EducationalPanel = ({ content }) => {
  if (!content) return null;
  
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <h4 className="text-xl font-bold text-blue-300">{content.topic}</h4>
      <p className="text-sm text-white/80 leading-relaxed">{content.explanation}</p>
      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
         <h5 className="text-xs font-bold text-white/40 uppercase mb-2">Did You Know?</h5>
         <p className="text-xs italic text-blue-200">{content.fact}</p>
      </div>
    </div>
  );
};

export default EducationalPanel;
