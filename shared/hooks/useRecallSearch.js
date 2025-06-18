import { useEffect, useState } from 'react';

export default function useRecallSearch(query) {
  const [results, setResults] = useState([]);
  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }
    fetch(`/api/recalls/search?q=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(setResults)
      .catch(() => setResults([]));
  }, [query]);
  return results;
}
