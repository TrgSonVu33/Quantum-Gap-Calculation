// api/client.ts

export const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface PredictResponse {
  formula: string;
  predicted_band_gap_ev: number;
  classification: string;
  timestamp: string;
}

export interface QueryRecord {
  id: number;
  formula: string;
  predicted_band_gap_ev: number;
  classification: string;
  created_at: string;
}

export interface HistoryResponse {
  total: number;
  queries: QueryRecord[];
}

export const apiClient = {
  async predict(formula: string): Promise<PredictResponse> {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ formula }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to predict band gap');
    }

    return response.json();
  },

  async getHistory(limit = 50, offset = 0): Promise<HistoryResponse> {
    const response = await fetch(`${API_BASE_URL}/history?limit=${limit}&offset=${offset}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch history');
    }

    return response.json();
  }
};
