import { useCallback, useState } from "react";
import { apiClient } from "../api/client";

export const useSummary = ({ currentConversationId, setIsProcessing }) => {
  const [summaryText, setSummaryText] = useState("");
  const [showSummaryModal, setShowSummaryModal] = useState(false);

  const handleGetSummary = useCallback(async () => {
    if (!currentConversationId) return;
    try {
      setIsProcessing(true);
      const summary = await apiClient.get(`/summary/${currentConversationId}`);
      setSummaryText(summary);
      setShowSummaryModal(true);
    } catch (error) {
      console.error("Summary Error:", error);
    } finally {
      setIsProcessing(false);
    }
  }, [currentConversationId, setIsProcessing]);

  return {
    summaryText,
    showSummaryModal,
    setShowSummaryModal,
    handleGetSummary,
  };
};
