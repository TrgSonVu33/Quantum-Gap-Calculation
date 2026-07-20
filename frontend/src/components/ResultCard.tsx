import { useState, useEffect } from 'react';
import type { PredictResponse } from '../api/client';

interface ResultCardProps {
  result: PredictResponse | null;
  isLoading: boolean;
}

export function ResultCard({ result, isLoading }: ResultCardProps) {
  const [stepText, setStepText] = useState('Đang xử lý...');

  useEffect(() => {
    if (!isLoading) return;

    setStepText('Đang thực hiện dự đoán qua Celery worker...');
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className="card glass-panel animate-fade-in result-display" style={{ height: '100%' }}>
        <div className="progress-spinner"></div>
        <div className="loading-text">{stepText}</div>
        <div className="loading-subtext">Vui lòng đợi giây lát</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="card glass-panel animate-fade-in" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
          Nhập công thức hóa học để dự đoán vùng cấm năng lượng.
        </p>
      </div>
    );
  }

  const getBadgeClass = (classification: string) => {
    switch (classification.toLowerCase()) {
      case 'metal': return 'badge-metal';
      case 'semiconductor': return 'badge-semiconductor';
      case 'insulator': return 'badge-insulator';
      default: return '';
    }
  };

  const translateClassification = (cls: string) => {
    switch (cls.toLowerCase()) {
      case 'metal': return 'Kim loại';
      case 'semiconductor': return 'Bán dẫn';
      case 'insulator': return 'Chất cách điện';
      default: return cls;
    }
  };

  let glowColor = 'var(--surface-border)';
  if (result.classification === 'Metal') glowColor = 'var(--color-metal)';
  if (result.classification === 'Semiconductor') glowColor = 'var(--color-semiconductor)';
  if (result.classification === 'Insulator') glowColor = 'var(--color-insulator)';

  return (
    <div 
      className="card glass-panel animate-fade-in result-display"
      style={{
        boxShadow: `0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 20px ${glowColor}22`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}
    >
      <h3 style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', fontFamily: 'monospace' }}>
        {result.formula}
      </h3>
      
      <div className="result-value" style={{ 
        background: `linear-gradient(135deg, ${glowColor}, #ffffff)`,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        {result.predicted_band_gap_ev.toFixed(2)} <span className="result-unit">eV</span>
      </div>
      
      <div className={`badge ${getBadgeClass(result.classification)}`}>
        {translateClassification(result.classification)}
      </div>
    </div>
  );
}
