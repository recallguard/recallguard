import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

jest.mock('html5-qrcode', () => ({
  Html5QrcodeScanner: function () {
    this.render = (onSuccess) => {
      onSuccess('12345');
    };
    this.clear = jest.fn().mockResolvedValue();
  },
}));

import ScanPage from '../pages/scan.jsx';

test('displays safe message after scanning', async () => {
  global.fetch = jest.fn().mockResolvedValue({ json: async () => ({ status: 'safe' }) });
  render(<ScanPage />);
  expect(await screen.findByText(/Safe/)).toBeInTheDocument();
});
