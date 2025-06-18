import { useEffect, useState } from 'react';
import { useTranslation } from 'next-i18next';

export default function Transparency() {
  const { t } = useTranslation('common');
  const [status, setStatus] = useState(null);
  const [latency, setLatency] = useState(null);

  useEffect(() => {
    fetch('/healthz')
      .then((r) => r.json())
      .then((d) => setStatus(d.status));
    fetch('/latency')
      .then((r) => r.json())
      .then((d) => setLatency(d.average_latency_seconds));
  }, []);

  return (
    <div>
      <h2>{t('transparency')}</h2>
      <h3>{t('data_sources')}</h3>
      <ul>
        <li>CPSC</li>
        <li>NHTSA</li>
        <li>FDA Enforcement Reports</li>
      </ul>
      <h3>{t('uptime_status')}</h3>
      <p>{status ? (status === 'ok' ? t('status_ok') : t('status_error')) : '...'}</p>
      <h3>{t('avg_latency')}</h3>
      <p>{latency !== null ? (latency / 3600).toFixed(1) + 'h' : '...'}</p>
    </div>
  );
}
