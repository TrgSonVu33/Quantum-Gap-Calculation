import { useState } from 'react';
import { HistoryTable } from './HistoryTable';
import type { QueryRecord } from '../api/client';

const classificationLabel: Record<string, string> = {
  metal: 'Kim loại',
  semiconductor: 'Bán dẫn',
  insulator: 'Chất cách điện',
};

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}

function StatCard({ label, value, sub, accent = 'var(--accent-cyan)' }: StatCardProps) {
  return (
    <div className="card glass-panel" style={{ padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontFamily: '"Outfit", sans-serif', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </div>
      <div style={{ fontSize: '2.25rem', fontWeight: 700, fontFamily: '"Outfit", sans-serif', color: accent, lineHeight: 1.1 }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{sub}</div>
      )}
    </div>
  );
}

export function DashboardPage() {
  const [queries, setQueries] = useState<QueryRecord[]>([]);

  const total = queries.length;
  const avgBg = total > 0
    ? (queries.reduce((s, q) => s + q.predicted_band_gap_ev, 0) / total).toFixed(3)
    : '—';

  const classCounts = queries.reduce<Record<string, number>>((acc, q) => {
    const k = q.classification.toLowerCase();
    acc[k] = (acc[k] ?? 0) + 1;
    return acc;
  }, {});
  const topClass = total > 0
    ? Object.entries(classCounts).sort((a, b) => b[1] - a[1])[0]
    : null;

  const classAccentMap: Record<string, string> = {
    metal: 'var(--color-metal)',
    semiconductor: 'var(--color-semiconductor)',
    insulator: 'var(--color-insulator)',
  };

  return (
    <div className="app-container animate-fade-in">
      <header className="hero-section">
        <h1 className="hero-title">Dashboard</h1>
        <p className="hero-subtitle">
          Lịch sử toàn bộ các dự đoán Band Gap đã thực hiện.
        </p>
      </header>

      {/* Stats Bar */}
      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
        <StatCard
          label="Tổng dự đoán"
          value={total > 0 ? String(total) : '—'}
          sub="bản ghi đã lưu"
          accent="var(--accent-cyan)"
        />
        <StatCard
          label="Band Gap trung bình"
          value={avgBg}
          sub="eV"
          accent="var(--accent-blue)"
        />
        <StatCard
          label="Phổ biến nhất"
          value={topClass ? (classificationLabel[topClass[0]] ?? topClass[0]) : '—'}
          sub={topClass ? `${topClass[1]} lần (${Math.round((topClass[1] / total) * 100)}%)` : undefined}
          accent={topClass ? classAccentMap[topClass[0]] : 'var(--text-secondary)'}
        />
      </div>

      <main>
        <HistoryTable refreshTrigger={0} showAll onDataLoaded={setQueries} />
      </main>
    </div>
  );
}
