import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../components/AuthContext.jsx';

export function useSubscriptions() {
  const { token } = useContext(AuthContext);
  const [subs, setSubs] = useState([]);

  useEffect(() => {
    if (!token) return;
    fetch('/api/subscriptions/', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setSubs);
  }, [token]);

  const remove = async (id) => {
    await fetch(`/api/subscriptions/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    setSubs((s) => s.filter((x) => x.id !== id));
  };

  return { subs, remove };
}
