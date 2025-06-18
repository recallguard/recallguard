import { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

export default function ScanPage() {
  const divId = useRef('qr-reader');
  const [result, setResult] = useState(null);

  useEffect(() => {
    const scanner = new Html5QrcodeScanner(divId.current, { fps: 10, qrbox: 250 });
    scanner.render(
      (text) => {
        scanner.clear();
        fetch(`/api/check/${encodeURIComponent(text)}`)
          .then((r) => r.json())
          .then((data) => setResult(data))
          .catch(() => {});
      },
      () => {}
    );
    return () => {
      scanner.clear().catch(() => {});
    };
  }, []);

  return (
    <div style={{ height: '100vh' }}>
      <div id={divId.current} />
      {result && (
        result.status === 'recalled' ? (
          <div>
            ⚠️ Recalled– <a href={result.url}>Details</a>
          </div>
        ) : (
          <div>
            ✅ Safe – No recalls found
          </div>
        )
      )}
    </div>
  );
}
