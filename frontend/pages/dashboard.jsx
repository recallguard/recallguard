import { useEffect, useState } from "react";

export default function Dashboard() {
  const [recalls, setRecalls] = useState([]);

  useEffect(() => {
    fetch("/api/recalls")
      .then((r) => r.json())
      .then((data) => setRecalls(data))
      .catch(() => setRecalls([]));
  }, []);

  const badgeClass = (src) => {
    const base = "px-2 py-1 rounded text-white text-xs";
    if (src === "CPSC") return `${base} bg-indigo-500`;
    if (src === "FDA") return `${base} bg-rose-500`;
    if (src === "NHTSA") return `${base} bg-amber-500`;
    return `${base} bg-gray-500`;
  };

  return (
    <div className="p-4">
      <h1 className="text-lg font-bold mb-2">Recent Recalls</h1>
      {recalls.length === 0 ? (
        <div>No recalls</div>
      ) : (
        <table className="min-w-full text-sm">
          <thead>
            <tr>
              <th className="text-left">Date</th>
              <th className="text-left">Product</th>
              <th className="text-left">Hazard</th>
              <th className="text-left">Source</th>
            </tr>
          </thead>
          <tbody>
            {recalls.map((r) => (
              <tr key={r.id} className="border-b">
                <td>{r.recall_date}</td>
                <td>{r.product}</td>
                <td title={r.hazard}>
                  {r.hazard && r.hazard.length > 80
                    ? `${r.hazard.slice(0, 80)}…`
                    : r.hazard}
                </td>
                <td>
                  <span className={badgeClass(r.source)}>{r.source}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

