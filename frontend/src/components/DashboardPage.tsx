import { HistoryTable } from './HistoryTable';

/**
 * Dashboard page — shows the full prediction history.
 * refreshTrigger is always 0 here since predictions happen on Home;
 * the table self-fetches on mount and whenever the user navigates back.
 */
export function DashboardPage() {
  return (
    <div className="app-container animate-fade-in">
      <header className="hero-section">
        <h1 className="hero-title">Dashboard</h1>
        <p className="hero-subtitle">
          Lịch sử toàn bộ các dự đoán Band Gap đã thực hiện.
        </p>
      </header>

      <main>
        <HistoryTable refreshTrigger={0} showAll />
      </main>
    </div>
  );
}
