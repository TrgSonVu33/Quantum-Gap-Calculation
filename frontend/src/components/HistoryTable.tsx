import { useEffect, useState } from 'react';
import { apiClient, type QueryRecord } from '../api/client';

export function HistoryTable({ refreshTrigger, showAll = false }: { refreshTrigger: number; showAll?: boolean }) {
  const [queries, setQueries] = useState<QueryRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await apiClient.getHistory(showAll ? 200 : 10);
        setQueries(data.queries);
      } catch (err) {
        console.error('Failed to load history', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [refreshTrigger]);

  if (loading) return (
    <div className="history-section animate-fade-in" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
      Đang tải lịch sử…
    </div>
  );
  if (queries.length === 0) return (
    <div className="history-section animate-fade-in" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
      Chưa có dự đoán nào được lưu.
    </div>
  );

  const translateClassification = (cls: string) => {
    switch (cls.toLowerCase()) {
      case 'metal': return 'Kim loại';
      case 'semiconductor': return 'Bán dẫn';
      case 'insulator': return 'Chất cách điện';
      default: return cls;
    }
  };

  return (
    <div className="history-section animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <h2 className="card-title">Lịch Sử Dự Đoán</h2>
      <div className="history-table-wrapper">
        <table className="styled-table">
          <thead>
            <tr>
              <th>Công thức</th>
              <th>Vùng cấm năng lượng (eV)</th>
              <th>Phân loại</th>  
            </tr>
          </thead>
          <tbody>
            {queries.map((q) => (
              <tr key={q.id}>
                <td className="formula-cell">{q.formula}</td>
                <td>{q.predicted_band_gap_ev.toFixed(2)}</td>
                <td>
                  <span style={{ 
                    color: `var(--color-${q.classification.toLowerCase()})`,
                    fontWeight: 500
                  }}>
                    {translateClassification(q.classification)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
