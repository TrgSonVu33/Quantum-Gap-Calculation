import { useEffect, useState } from 'react';
import { apiClient, type QueryRecord } from '../api/client';

interface Props {
  refreshTrigger: number;
  showAll?: boolean;
  onDataLoaded?: (queries: QueryRecord[]) => void;
}

const translateClassification = (cls: string) => {
  switch (cls.toLowerCase()) {
    case 'metal': return 'Kim loại';
    case 'semiconductor': return 'Bán dẫn';
    case 'insulator': return 'Chất cách điện';
    default: return cls;
  }
};

const formatDate = (iso: string) => {
  const d = new Date(iso);
  return d.toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

export function HistoryTable({ refreshTrigger, showAll = false, onDataLoaded }: Props) {
  const [queries, setQueries] = useState<QueryRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const data = await apiClient.getHistory(showAll ? 200 : 10);
        setQueries(data.queries);
        onDataLoaded?.(data.queries);
      } catch (err) {
        console.error('Failed to load history', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [refreshTrigger]);

  if (loading) return (
    <div className="history-section animate-fade-in" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
      <div className="progress-spinner" style={{ margin: '0 auto 1rem' }} />
      <p>Đang tải lịch sử…</p>
    </div>
  );

  if (queries.length === 0) return (
    <div className="history-section animate-fade-in" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
      <p style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔬</p>
      <p>Chưa có dự đoán nào được lưu.</p>
    </div>
  );

  return (
    <div className="history-section animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>Lịch Sử Dự Đoán</h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.05)', padding: '0.3rem 0.75rem', borderRadius: '20px', border: '1px solid var(--surface-border)' }}>
          {queries.length} bản ghi
        </span>
      </div>
      <div className="history-table-wrapper">
        <table className="styled-table">
          <thead>
            <tr>
              <th style={{ width: '3rem', textAlign: 'center' }}>#</th>
              <th>Công thức</th>
              <th>Vùng cấm (eV)</th>
              <th>Phân loại</th>
              <th>Thời gian</th>
            </tr>
          </thead>
          <tbody>
            {queries.map((q, i) => (
              <tr key={q.id}>
                <td style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{i + 1}</td>
                <td className="formula-cell">{q.formula}</td>
                <td style={{ fontFamily: '"Outfit", sans-serif', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {q.predicted_band_gap_ev.toFixed(3)}
                </td>
                <td>
                  <span className={`badge badge-${q.classification.toLowerCase()}`}>
                    {translateClassification(q.classification)}
                  </span>
                </td>
                <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
                  {formatDate(q.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
