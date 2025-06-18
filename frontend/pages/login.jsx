import { useState, useContext } from 'react';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import { AuthContext } from '../components/AuthContext.jsx';
import { apiFetch } from '../utils/api.js';

export default function Login() {
  const router = useRouter();
  const { t } = useTranslation('common');
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await apiFetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (res.ok) {
      const data = await res.json();
      login(data.token);
      router.push('/');
    } else {
      setError(t('invalid_credentials'));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t('email')}
        />
      </div>
      <div>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t('password')}
        />
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit">{t('login')}</button>
    </form>
  );
}
