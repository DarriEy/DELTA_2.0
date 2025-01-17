import React, { useState } from 'react';

const SummaryModal = ({ summary, onConfirm, onCancel }) => {
  const [editedSummary, setEditedSummary] = useState(summary);

  const handleSummaryChange = (event) => {
    setEditedSummary(event.target.value);
  };

  const handleConfirm = () => {
    onConfirm(editedSummary);
  };

  return (
    <div className="summary-modal">
      <h2>End of Day Summary</h2>
      <textarea
        value={editedSummary}
        onChange={handleSummaryChange}
        rows={10}
        cols={50}
      />
      <div className="summary-buttons">
        <button onClick={handleConfirm}>Confirm</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
};

export default SummaryModal;
