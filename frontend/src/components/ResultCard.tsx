import { useState, useEffect, useRef } from 'react';
import type { PredictResponse } from '../api/client';
import * as $3Dmol from '3dmol';

interface ResultCardProps {
  result: PredictResponse | null;
  isLoading: boolean;
}

export function ResultCard({ result, isLoading }: ResultCardProps) {
  const [stepText, setStepText] = useState('Đang xử lý...');
  const viewerRef = useRef<HTMLDivElement>(null);
  const viewerInstance = useRef<any>(null);

  useEffect(() => {
    if (!isLoading) return;

    setStepText('Đang thực hiện dự đoán qua Celery worker...');
  }, [isLoading]);

  // Handle 3Dmol viewer when result changes
  useEffect(() => {
    if (result && viewerRef.current) {
      if (!viewerInstance.current) {
        viewerInstance.current = $3Dmol.createViewer(viewerRef.current, {
          backgroundColor: 'white'
        });
      }

      const viewer = viewerInstance.current;
      viewer.clear();

      const fetchStructure = async () => {
        try {
          const dummyCif = `
data_dummy
_cell_length_a 5.0
_cell_length_b 5.0
_cell_length_c 5.0
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
loop_
_atom_site_label
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
A 0.0 0.0 0.0
B 0.5 0.5 0.5
`;
          viewer.addModel(dummyCif, "cif");
          viewer.setStyle({}, { sphere: { radius: 0.5 }, stick: { radius: 0.2 } });
          viewer.zoomTo();
          viewer.render();
        } catch (error) {
          console.error("Failed to load 3D structure", error);
        }
      };

      fetchStructure();
    }
  }, [result]);

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
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '2rem'
      }}
    >
      <div style={{ flex: 1 }}>
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

      <div style={{ flex: 1, height: '200px', position: 'relative' }}>
        <div ref={viewerRef} style={{ width: '100%', height: '100%', borderRadius: '8px', overflow: 'hidden' }}></div>
        <div style={{ position: 'absolute', bottom: '5px', left: '0', right: '0', textAlign: 'center', fontSize: '0.7rem', color: 'gray' }}>
          Minh họa cấu trúc mạng (3Dmol)
        </div>
      </div>
    </div>
  );
}
