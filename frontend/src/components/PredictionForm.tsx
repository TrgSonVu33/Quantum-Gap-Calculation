import { useState } from 'react';

interface PredictionFormProps {
  onSubmit: (formula: string) => Promise<void>;
  isLoading: boolean;
}

export function PredictionForm({ onSubmit, isLoading }: PredictionFormProps) {
  const [formula, setFormula] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const trimmed = formula.trim();
    if (!trimmed) {
      setError('Vui lòng nhập công thức hóa học');
      return;
    }

    // Basic client-side validation (must start with uppercase letter)
    if (!/^[A-Z]/.test(trimmed)) {
      setError('Công thức hóa học phải bắt đầu bằng ký hiệu nguyên tố viết hoa (ví dụ: Ga, Na, Fe)');
      return;
    }

    try {
      await onSubmit(trimmed);
      setFormula(''); // clear on success
    } catch (err: any) {
      setError(err.message || 'Đã xảy ra lỗi trong quá trình dự đoán');
    }
  };

  return (
    <div className="card glass-panel animate-fade-in">
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
    </div>
  );
}
