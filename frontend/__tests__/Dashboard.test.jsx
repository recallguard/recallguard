import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../pages/dashboard.jsx';

beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve([
        {
          id: 1,
          product: 'Widget',
          hazard: 'Fire hazard',
          recall_date: '2024-01-01',
          source: 'CPSC',
          url: 'https://example.com'
        }
      ])
    })
  );
});

afterEach(() => {
  fetch.mockClear();
});

test('dashboard renders recall row', async () => {
  render(<Dashboard />);
  await waitFor(() => screen.getByText('Widget'));
  expect(screen.getByText('Widget')).toBeInTheDocument();
});
