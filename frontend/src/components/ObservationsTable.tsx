import type { Observation } from "../api";
import { formatDateTime } from "../utils/formatDateTime";

export function ObservationsTable({
  observations,
  loading,
}: {
  observations: Observation[];
  loading: boolean;
}) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden flex-1 flex flex-col min-h-0">
      <div className="px-4 py-3 border-b border-slate-200">
        <h2 className="text-sm font-bold text-slate-700">気象データ履歴一覧</h2>
      </div>

      {loading ? (
        <p className="text-slate-500 p-4">読み込み中...</p>
      ) : observations.length === 0 ? (
        <p className="text-slate-500 p-4">データがありません</p>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-100 text-slate-600 sticky top-0">
              <tr>
                <th className="px-4 py-2 text-left font-medium">日時(降順)</th>
                <th className="px-4 py-2 text-right font-medium">気温(℃)</th>
                <th className="px-4 py-2 text-right font-medium">風速(m/s)</th>
                <th className="px-4 py-2 text-right font-medium">風向</th>
                <th className="px-4 py-2 text-right font-medium">
                  降水量(mm/h)
                </th>
              </tr>
            </thead>
            <tbody>
              {observations.map((o) => (
                <tr
                  key={o.datetime}
                  className="border-t border-slate-100 hover:bg-slate-50"
                >
                  <td className="px-4 py-2 text-slate-700">
                    {formatDateTime(o.datetime)}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {o.temperature ?? "-"}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {o.wind_speed ?? "-"}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {o.wind_direction ?? "-"}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {o.precipitation ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
