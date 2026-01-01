import { describe, it, expect, vi, beforeEach } from 'vitest';
import { submitModelingJob, getJobStatus } from '../modeling';
import { apiClient } from '../client';

vi.mock('../client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('modeling api', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('submitModelingJob calls /run_modeling with correct payload', async () => {
    const mockResponse = { message: 'ok', job_id: 123 };
    vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

    const result = await submitModelingJob('SUMMA');

    expect(apiClient.post).toHaveBeenCalledWith('/run_modeling', {
      type: 'SIMULATION',
      parameters: {
        model: 'SUMMA',
        watershed: "Bow_at_Banff_lumped",
      },
    });
    expect(result).toEqual(mockResponse);
  });

  it('getJobStatus calls /jobs/{id}', async () => {
    const mockResponse = { id: 123, status: 'COMPLETED' };
    vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

    const result = await getJobStatus(123);

    expect(apiClient.get).toHaveBeenCalledWith('/jobs/123');
    expect(result).toEqual(mockResponse);
  });
});
