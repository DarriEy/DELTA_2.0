import { useCallback, useState } from "react";
import { submitModelingJob } from "../api/modeling";

export const useModelingJob = ({ setIsProcessing, onShake }) => {
  const [jobStatus, setJobStatus] = useState(null);

  const handleModelingJobSubmit = useCallback(
    async (selectedModel) => {
      try {
        setIsProcessing(true);
        const response = await submitModelingJob(selectedModel);
        setJobStatus("PENDING");
        return response;
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
