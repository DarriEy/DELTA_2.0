import { useCallback, useState } from "react";
import { apiClient } from "../api/client";

export const useModelingJob = ({ setIsProcessing, onShake }) => {
  const [jobStatus, setJobStatus] = useState(null);

  const handleModelingJobSubmit = useCallback(
    async (selectedModel) => {
      try {
        setIsProcessing(true);
        await apiClient.post("/run_modeling", {
          model: selectedModel,
          job_type: "SIMULATION",
        });
        setJobStatus("PENDING");
      } catch (error) {
        console.error("Modeling Error:", error);
        onShake();
      } finally {
        setIsProcessing(false);
      }
    },
    [setIsProcessing, onShake]
  );

  return { jobStatus, handleModelingJobSubmit };
};
