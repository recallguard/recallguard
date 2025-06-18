import { useEffect, useState, useContext } from 'react';
import { AuthContext } from '../components/AuthContext.jsx';
import { apiFetch } from '../utils/api.js';

const labels = { self: 'Me', child: 'My Kids', pet: 'My Pets', other: 'Other' };

export default function MyStuff() {
  const { token } = useContext(AuthContext);
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ upc: '', label: '', profile: 'self' });
  const [error, setError] = useState(null);

  const load = async () => {
    const res = await apiFetch('/api/items');
    if (res.ok) setItems(await res.json());
  };

  useEffect(() => {
    if (token) load();
    const id = setInterval(() => token && load(), 30000);
    return () => clearInterval(id);
  }, [token]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.upc) { setError('UPC required'); return; }
    const res = await apiFetch('/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (res.ok) {
      setForm({ upc: '', label: '', profile: 'self' });
      setError(null);
      load();
    }
  };

  const remove = async (id) => {
    await apiFetch(`/api/items/${id}`, { method: 'DELETE' });
    setItems((it) => it.filter((x) => x.id !== id));
  };

  const groups = {};
  items.forEach((i) => { (groups[i.profile] = groups[i.profile] || []).push(i); });

  return (
    <div>
      <form onSubmit={onSubmit} aria-label="add-form">
        <input
          placeholder="UPC"
          value={form.upc}
          onChange={(e) => setForm({ ...form, upc: e.target.value })}
        />
        <input
          placeholder="Label"
          value={form.label}
          onChange={(e) => setForm({ ...form, label: e.target.value })}
        />
        <select
          value={form.profile}
          onChange={(e) => setForm({ ...form, profile: e.target.value })}
        >
          <option value="self">Me</option>
          <option value="child">My Kids</option>
          <option value="pet">My Pets</option>
          <option value="other">Other</option>
        </select>
        <button type="submit">Add</button>
        {error && <span>{error}</span>}
      </form>

      {Object.entries(groups).map(([p, list]) => (
        <div key={p}>
          <h3>{labels[p] || p}</h3>
          <ul>
            {list.map((it) => (
              <li key={it.id}>
                {it.label || it.upc} - {it.status === 'recalled' ? '⚠️ Recalled' : '✅ Safe'}
                <button onClick={() => remove(it.id)}>Delete</button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
