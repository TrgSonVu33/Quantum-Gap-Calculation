import { useState } from 'react';
import { PredictionForm } from './components/PredictionForm';
import { ResultCard } from './components/ResultCard';
import { HistoryTable } from './components/HistoryTable';
import { apiClient, type PredictResponse } from './api/client';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [historyTrigger, setHistoryTrigger] = useState(0);

  const handlePredict = async (formula: string) => {
    setLoading(true);
    setResult(null); // Clear previous result to show the calculation process
    
    const fetchPromise = apiClient.predict(formula);
    const delayPromise = new Promise(resolve => setTimeout(resolve, 15000));

    try {
      const [response] = await Promise.all([fetchPromise, delayPromise]);
      setResult(response);
      setHistoryTrigger(prev => prev + 1); // trigger history refresh
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="hero-section animate-fade-in">
        <h1 className="hero-title">Quantum Gap Calculation</h1>
        <p className="hero-subtitle">
          Dự đoán tức thời vùng cấm năng lượng (Band Gap) của các vật liệu vô cơ từ công thức hóa học sử dụng mô hình Random Forest được huấn luyện trên Materials Project.
        </p>
      </header>

      <main className="main-content">
        <PredictionForm onSubmit={handlePredict} isLoading={loading} />
        <ResultCard result={result} isLoading={loading} />
      </main>

      <div className="info-grid animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div className="card glass-panel info-card">
          <h3 className="card-title">Tại sao cần dự đoán Eg?</h3>
          <p>
            Vùng cấm năng lượng (Band Gap - Eg) quyết định khả năng dẫn điện của vật liệu, từ đó định hình ứng dụng thực tế:
          </p>
          <div className="steps-accordion" style={{ margin: '1rem 0' }}>
            <details>
              <summary>Eg thấp hoặc bằng 0 (≤ 3.0 eV)</summary>
              <p>
                Electron dễ di chuyển. Vật liệu dẫn điện rất tốt (Kim loại) hoặc có tính bán dẫn (Bán dẫn) - ứng dụng rộng rãi trong pin mặt trời, LED và chip máy tính.
              </p>
            </details>
            <details>
              <summary>Eg cao (&gt; 3.0 eV)</summary>
              <p>
                Cần năng lượng cực lớn để kích hoạt electron. Vật liệu không dẫn điện (Chất cách điện) - phù hợp làm lớp phủ bảo vệ, gốm sứ chịu nhiệt cao và tụ điện cách điện.
              </p>
            </details>
          </div>
          <p>
            Dự đoán Eg giúp sàng lọc nhanh hàng triệu công thức hóa học chỉ trong vài giây thay vì mất nhiều tuần tính toán mô phỏng vật lý phức tạp (DFT) hay thực nghiệm trong phòng thí nghiệm.
          </p>
        </div>

        <div className="card glass-panel info-card">
          <h3 className="card-title">Quy trình dự đoán hoạt động thế nào?</h3>
          <div className="steps-accordion">
            <details>
              <summary>1. Phân tích Công thức</summary>
              <p>
                Sử dụng <code>pymatgen</code> để phân tích công thức hóa học do bạn nhập và tính toán tỷ lệ phần trăm nguyên tố cấu thành vật liệu.
              </p>
            </details>
            <details>
              <summary>2. Trích xuất Đặc trưng</summary>
              <p>
                Tạo ra 132 đặc trưng Magpie từ cơ sở dữ liệu hóa học (bao gồm độ âm điện trung bình, bán kính nguyên tử, số electron hóa trị...).
              </p>
            </details>
            <details>
              <summary>3. Dự đoán bằng AI</summary>
              <p>
                Các đặc trưng được đưa qua mô hình Random Forest Regressor đã huấn luyện trên 5.000 vật liệu thực tế từ Materials Project để đưa ra giá trị Eg chính xác.
              </p>
            </details>
          </div>
        </div>
      </div>

      <section>
        <HistoryTable refreshTrigger={historyTrigger} />
      </section>
    </div>
  );
}

export default App;
