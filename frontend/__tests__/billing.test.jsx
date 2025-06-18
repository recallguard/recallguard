import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import Billing from '../pages/settings/billing.jsx';
import { AuthContext } from '../components/AuthContext.jsx';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ url: '/checkout' }) });
});

test('billing page renders and triggers checkout', async () => {
  render(
    <AuthContext.Provider value={{ token: 't' }}>
      <Billing />
    </AuthContext.Provider>
  );
  fireEvent.click(screen.getByText('Upgrade to Pro'));
  expect(fetch).toHaveBeenCalledWith('/api/billing/checkout', expect.objectContaining({ method: 'POST' }));
});
