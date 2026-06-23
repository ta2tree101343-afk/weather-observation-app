import { useWeatherData } from "./hooks/useWeatherData";
import { formatDateTime } from "./utils/formatDateTime";
import { StatCard } from "./components/StatCard";
import { WardSelect } from "./components/WardSelect";
import { ObservationsTable } from "./components/ObservationsTable";

function App() {
  const {
    wards,
    wardsLoading,
    selectedWard,
    setSelectedWard,
    observations,
    loading,
    errors,
  } = useWeatherData();

  const selectedName = wards.find((w) => w.code === selectedWard)?.name ?? "-";
  const latest = observations[0];

  return (
    <div className="h-screen flex flex-col bg-slate-100">
      <header className="bg-slate-800 text-white px-6 py-4 sticky top-0 z-10">
        <h1 className="text-lg font-bold">気象データ管理システム</h1>
      </header>

      <main className="max-w-5xl w-full mx-auto p-6 space-y-6 flex-1 flex flex-col min-h-0">
        {errors.wards && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            区一覧の取得に失敗しました: {errors.wards.message}
          </div>
        )}
        {errors.observations && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            観測データの取得に失敗しました: {errors.observations.message}
          </div>
        )}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="対象地域" value={selectedName} />
          <StatCard
            label="最終観測"
            value={latest ? formatDateTime(latest.datetime) : "-"}
          />
          <StatCard
            label="最新気温"
            value={
              latest?.temperature != null ? `${latest.temperature} ℃` : "-"
            }
          />
          <StatCard label="取得件数" value={`${observations.length} 件`} />
        </div>

        <div className="bg-white rounded-lg border border-slate-200 p-4 flex items-center gap-3">
          <span className="text-sm font-medium text-slate-700">対象区:</span>
          {wardsLoading ? (
            <span className="text-sm text-slate-400">読み込み中...</span>
          ) : (
            <WardSelect
              wards={wards}
              selected={selectedWard}
              onChange={setSelectedWard}
            />
          )}
        </div>

        <ObservationsTable observations={observations} loading={loading} />
      </main>
    </div>
  );
}

export default App;
