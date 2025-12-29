import React, { useState } from 'react';

const SummaryModal = ({ summary, onConfirm, onCancel }) => {
  const [editedSummary, setEditedSummary] = useState(summary);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="glass-card w-full max-w-2xl p-8 relative transform transition-all scale-100">
        
        {/* Header */}
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500 mb-2">
            Session Summary
        </h2>
        <p className="text-sm text-white/60 mb-6">
            Review and edit the key points from today's session before saving.
        </p>

        {/* Text Area */}
        <div className="bg-black/30 rounded-xl p-2 border border-white/10 mb-6 focus-within:border-orange-500/50 transition-colors">
            <textarea
                value={editedSummary}
                onChange={(e) => setEditedSummary(e.target.value)}
                rows={12}
                className="w-full bg-transparent text-slate-200 text-sm p-3 focus:outline-none resize-none leading-relaxed"
                placeholder="Summary content..."
            />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3">
            <button 
                onClick={onCancel}
                className="px-5 py-2 rounded-lg text-sm font-medium text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            >
                Cancel
            </button>
            <button 
                onClick={() => onConfirm(editedSummary)}
                className="px-6 py-2 rounded-lg text-sm font-bold bg-gradient-to-r from-orange-500 to-red-600 text-white shadow-lg hover:shadow-orange-500/30 hover:scale-105 active:scale-95 transition-all"
            >
                Save & End
            </button>
        </div>

      </div>
    </div>
  );
};

export default SummaryModal;