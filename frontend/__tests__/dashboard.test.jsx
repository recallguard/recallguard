import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../pages/dashboard.jsx';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    json: async () => [
      { id: 1, product: 'Widget', hazard: 'Fire hazard', recall_date: '2024-04-01', source: 'cpsc' }
    ]
  });
});

test('renders recall table', async () => {
  render(<Dashboard />);
  expect(await screen.findByText('Widget')).toBeInTheDocument();
});
