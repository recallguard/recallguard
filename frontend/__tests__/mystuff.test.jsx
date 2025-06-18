import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import MyStuff from '../pages/mystuff.jsx';
import { AuthContext } from '../components/AuthContext.jsx';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({ json: async () => [] });
});

test('shows grouped items', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => [
      { id: 1, upc: '1', profile: 'self', status: 'safe' },
      { id: 2, upc: '2', profile: 'pet', status: 'recalled' }
    ]
  });
  render(
    <AuthContext.Provider value={{ token: 't' }}>
      <MyStuff />
    </AuthContext.Provider>
  );
  expect(await screen.findByText('My Pets')).toBeInTheDocument();
  expect(screen.getByText('Me')).toBeInTheDocument();
});

test('form requires upc', async () => {
  render(
    <AuthContext.Provider value={{ token: 't' }}>
      <MyStuff />
    </AuthContext.Provider>
  );
  fireEvent.submit(screen.getByLabelText('add-form'));
  expect(await screen.findByText('UPC required')).toBeInTheDocument();
});

