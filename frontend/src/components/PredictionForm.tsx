import { useState } from 'react';
import type { DragEvent } from 'react';
import Papa from 'papaparse';

interface PredictionFormProps {
  onSubmit: (formula: string) => Promise<void>;
  onBatchSubmit?: (formulas: string[]) => Promise<void>;
  isLoading: boolean;
}

export function PredictionForm({ onSubmit, onBatchSubmit, isLoading }: PredictionFormProps) {
  const [formula, setFormula] = useState('');
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const trimmed = formula.trim();
    if (!trimmed) {
      setError('Vui lòng nhập công thức hóa học');
      return;
    }

    if (!/^[A-Z]/.test(trimmed)) {
      setError('Công thức hóa học phải bắt đầu bằng ký hiệu nguyên tố viết hoa (ví dụ: Ga, Na, Fe)');
      return;
    }

    try {
      await onSubmit(trimmed);
      setFormula('');
    } catch (err: any) {
      setError(err.message || 'Đã xảy ra lỗi trong quá trình dự đoán');
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    setError('');

    if (isLoading) return;

    const file = e.dataTransfer.files[0];
    if (!file) return;
    
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setError('Vui lòng tải lên file CSV');
      return;
    }

    if (!onBatchSubmit) {
      setError('Tính năng dự đoán hàng loạt chưa được hỗ trợ.');
      return;
    }

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results: any) => {
        try {
          const rows = results.data as any[];
          // Try to find a column named 'formula' or use the first column
          const formulas: string[] = [];
          
          if (rows.length > 0) {
            const keys = Object.keys(rows[0]);
            const formulaKey = keys.find(k => k.toLowerCase() === 'formula') || keys[0];
            
            for (const row of rows) {
              if (row[formulaKey] && typeof row[formulaKey] === 'string') {
                const f = row[formulaKey].trim();
                if (f) formulas.push(f);
              }
            }
          }

          if (formulas.length === 0) {
            setError('Không tìm thấy công thức nào trong file CSV.');
            return;
          }

          if (formulas.length > 100) {
            setError('Giới hạn 100 công thức mỗi lần upload.');
            return;
          }

          await onBatchSubmit(formulas);
        } catch (err: any) {
          setError(err.message || 'Lỗi xử lý file CSV');
        }
      },
      error: (error: any) => {
        setError(`Lỗi đọc file: ${error.message}`);
      }
    });
  };

  return (
    <div 
      className={`card glass-panel animate-fade-in ${isDragging ? 'drag-active' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{ border: isDragging ? '2px dashed var(--primary-color)' : '' }}
    >
      <h2 className="card-title">Dự Đoán Vùng Cấm Năng Lượng</h2>
      <form onSubmit={handleSubmit} className="input-group">
        <div>
          <input
            type="text"
            className="styled-input"
            placeholder="ví dụ: GaAs, NaCl, Fe2O3"
            value={formula}
            onChange={(e) => {
              setFormula(e.target.value);
              setError('');
            }}
            disabled={isLoading}
            autoComplete="off"
            spellCheck="false"
          />
          {error && <div className="error-message">{error}</div>}
        </div>
        <button 
          type="submit" 
          className={`primary-button ${isLoading ? 'loading' : ''}`}
          disabled={isLoading || !formula.trim()}
        >
          {isLoading ? 'Đang tính toán...' : 'Dự đoán Eg'}
        </button>
      </form>
      <div style={{ marginTop: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
        <p>Hoặc kéo thả file CSV chứa cột 'formula' vào đây để dự đoán hàng loạt (tối đa 100).</p>
      </div>
    </div>
  );
}
