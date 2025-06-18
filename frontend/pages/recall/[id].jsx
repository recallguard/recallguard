import { useRouter } from 'next/router';
import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../../components/AuthContext.jsx';

export default function RecallDetail() {
  const router = useRouter();
  const { token } = useContext(AuthContext);
  const { id } = router.query;
  const [recall, setRecall] = useState(null);

  useEffect(() => {
    if (!id || !token) return;
    fetch(`/api/recall/${id}`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => setRecall(data))
      .catch(() => {});
  }, [id, token]);

  if (!recall) return <div>Loading...</div>;

  return (
    <div>
      <h2>{recall.product}</h2>
      <p>{recall.hazard}</p>
      <div aria-label="timeline">
        {recall.remedy_updates && recall.remedy_updates.map((u, i) => (
          <div key={i} style={{ borderLeft: '2px solid #ccc', marginLeft: '1em', paddingLeft: '1em' }}>
            <div>{u.time}</div>
            <p>{u.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
