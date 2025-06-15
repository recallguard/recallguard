import { useEffect, useState } from "react";

export default function RecallAlerts() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetch("/api/alerts?user=1")
      .then((r) => r.json())
      .then((data) => setAlerts(data))
      .catch(() => setAlerts([]));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-lg font-bold mb-2">Your Alerts</h1>
      {alerts.length === 0 ? (
        <div>No alerts yet</div>
      ) : (
        <ul>
          {alerts.map((a) => (
            <li key={a.id} className="mb-2">
              <strong>{a.product}</strong> - {a.hazard}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

