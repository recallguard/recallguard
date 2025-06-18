export async function checkCode(code) {
  const res = await fetch(`/api/check/${encodeURIComponent(code)}`);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}
