import { renderHook, act } from '@testing-library/react';
import { AuthContext } from '../components/AuthContext.jsx';
import { useSubscriptions } from '../hooks/useSubscriptions.js';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({ json: async () => [{ id: 1, recall_source: 'cpsc', product_query: 'Widget' }] });
});

test('fetches subscriptions on mount and delete works', async () => {
  const wrapper = ({ children }) => (
    <AuthContext.Provider value={{ token: 't' }}>{children}</AuthContext.Provider>
  );
  const { result } = renderHook(() => useSubscriptions(), { wrapper });
  await act(async () => {});
  expect(result.current.subs.length).toBe(1);
  fetch.mockResolvedValueOnce({});
  await act(async () => {
    await result.current.remove(1);
  });
  expect(result.current.subs.length).toBe(0);
});
