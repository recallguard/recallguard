import { useContext } from 'react';
import { AuthContext } from '../../components/AuthContext.jsx';
import { apiFetch } from '../../utils/api.js';

export default function Billing() {
  const { token } = useContext(AuthContext);
  const upgrade = async () => {
    const res = await apiFetch('/api/billing/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan: 'pro' })
    });
    if (res.ok) {
      const data = await res.json();
      window.location.href = data.url;
    }
  };
  return (
    <div>
      <h2>Billing</h2>
      {token && <button onClick={upgrade}>Upgrade to Pro</button>}
      <a href="/api/billing/portal">Manage subscription</a>
    </div>
  );
}
