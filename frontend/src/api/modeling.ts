import { apiClient } from './client';

export interface ModelingJobResponse {
  message: string;
  job_id: number;
}

export interface JobStatusResponse {
  id: number;
  type: string;
  status: string;
  result?: any;
  parameters: any;
  created_at: string;
  updated_at: string;
}

/**
 * Submit a modeling job to the backend.
 * @param {string} model - The model to run (e.g., 'SUMMA').
 * @param {string} type - The job type (default 'SIMULATION').
 * @returns {Promise<ModelingJobResponse>} The response data containing job_id.
 */
export async function submitModelingJob(model: string, type: string = 'SIMULATION'): Promise<ModelingJobResponse> {
  try {
    return await apiClient.post<ModelingJobResponse>('/run_modeling', {
      type,
      parameters: {
        model,
        watershed: "Bow_at_Banff_lumped",
      }
    });
  } catch (error) {
    console.error('submitModelingJob exception:', error);
    throw error;
  }
}

/**
 * Get job status from the backend.
 * @param {number} jobId - The job ID.
 */
export async function getJobStatus(jobId: number): Promise<JobStatusResponse> {
  return await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);
}