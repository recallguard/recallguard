import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
<<<<<<< HEAD
import Dashboard from '../pages/dashboard.jsx';
=======
import React from 'react';
jest.mock('@chakra-ui/react', () => {
  const React = require('react');
  return {
    ChakraProvider: ({ children }) => <div>{children}</div>,
    SimpleGrid: ({ children }) => <div>{children}</div>,
    Box: ({ children }) => <div>{children}</div>,
    Text: ({ children }) => <span>{children}</span>,
    Badge: ({ children }) => <span>{children}</span>,
    Flex: ({ children }) => <div>{children}</div>,
    Button: ({ children, ...props }) => <button {...props}>{children}</button>,
    IconButton: ({ children, ...props }) => <button {...props}>{children}</button>,
    useColorMode: () => ({ colorMode: 'light', toggleColorMode: () => {} })
  };
});
jest.mock('@chakra-ui/icons', () => ({ SunIcon: () => <span>sun</span>, MoonIcon: () => <span>moon</span> }));

import Dashboard from '../pages/dashboard.jsx';
import { ChakraProvider } from '@chakra-ui/react';
import { AuthProvider } from '../components/AuthContext.jsx';
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    json: async () => [
      { id: 1, product: 'Widget', hazard: 'Fire hazard', recall_date: '2024-04-01', source: 'cpsc' }
    ]
  });
});

<<<<<<< HEAD
test('renders recall table', async () => {
  render(<Dashboard />);
  expect(await screen.findByText('Widget')).toBeInTheDocument();
=======
test('renders recall cards with hazard badge', async () => {
  render(
    <ChakraProvider>
      <AuthProvider>
        <Dashboard />
      </AuthProvider>
    </ChakraProvider>
  );
  expect(await screen.findByText('Widget')).toBeInTheDocument();
  expect(screen.getByText('Fire hazard')).toBeInTheDocument();
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
});
