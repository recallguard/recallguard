import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [recalls, setRecalls] = useState(null);

  useEffect(() => {
    fetch('/api/recalls/recent')
      .then((res) => res.json())
      .then((data) => setRecalls(data))
      .catch(() => setRecalls([]));
  }, []);

  if (recalls === null) {
    return <div>Loading...</div>;
  }

  if (recalls.length === 0) {
    return (
      <div style={{ color: 'green' }}>
        No recent recalls.
      </div>
    );
  }

  const truncate = (text) =>
    text && text.length > 50 ? text.slice(0, 50) + '…' : text;

  const badgeColor = (source) => {
    const colors = {
      cpsc: '#FFB703',
      fda: '#8ECAE6',
      nhtsa: '#90BE6D',
      usda: '#FB8500'
    };
    return { backgroundColor: colors[source.toLowerCase()] || '#ddd', padding: '2px 6px', borderRadius: '4px', color: '#000' };
  };

  return (
    <table>
      <thead>
        <tr>
          <th>Product</th>
          <th>Hazard</th>
          <th>Date</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        {recalls.map((r) => (
          <tr key={`${r.source}-${r.id}`}>
            <td>{r.product}</td>
            <td>{truncate(r.hazard)}</td>
            <td>{r.recall_date}</td>
            <td>
              <span style={badgeColor(r.source)}>{r.source}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

