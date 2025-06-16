import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
jest.mock('@chakra-ui/react', () => {
  const React = require('react');
  return {
    ChakraProvider: ({ children }) => <div>{children}</div>,
    Box: ({ children }) => <div>{children}</div>,
    Table: ({ children }) => <table>{children}</table>,
    Thead: ({ children }) => <thead>{children}</thead>,
    Tbody: ({ children }) => <tbody>{children}</tbody>,
    Tr: ({ children, ...props }) => <tr {...props}>{children}</tr>,
    Th: ({ children }) => <th>{children}</th>,
    Td: ({ children }) => <td>{children}</td>,
    Badge: ({ children }) => <span>{children}</span>,
    Input: (props) => <input {...props} />,
    Drawer: ({ children }) => <div>{children}</div>,
    DrawerOverlay: ({ children }) => <div>{children}</div>,
    DrawerContent: ({ children }) => <div>{children}</div>,
    DrawerHeader: ({ children }) => <div>{children}</div>,
    DrawerBody: ({ children }) => <div>{children}</div>,
    Skeleton: () => <div>loading</div>,
    Center: ({ children }) => <div>{children}</div>,
    HStack: ({ children }) => <div>{children}</div>,
    Flex: ({ children }) => <div>{children}</div>,
    Spacer: () => <div />,
    IconButton: (props) => <button {...props} />,
    Button: ({ children, ...props }) => <button {...props}>{children}</button>,
    useDisclosure: () => ({ isOpen: false, onOpen: jest.fn(), onClose: jest.fn() }),
    useColorMode: () => ({ colorMode: 'light', toggleColorMode: () => {} }),
    Link: (props) => <a {...props} />,
  };
});
jest.mock('@chakra-ui/icons', () => ({ SunIcon: () => <span>sun</span>, MoonIcon: () => <span>moon</span> }));
jest.mock('@tanstack/react-virtual', () => ({ useVirtualizer: () => ({ getVirtualItems: () => [{ index: 0 }] }) }));
jest.mock('react-markdown', () => (props) => <div>{props.children}</div>);

import Dashboard from '../pages/dashboard.jsx';
import { ChakraProvider } from '@chakra-ui/react';
import { AuthProvider } from '../components/AuthContext.jsx';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    json: async () => [
      { id: 1, product: 'Widget', hazard: 'Fire hazard', recall_date: '2024-04-01', source: 'cpsc' }
    ]
  });
});


test('renders table rows after fetch', async () => {
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
});

