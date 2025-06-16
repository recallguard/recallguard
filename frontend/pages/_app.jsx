
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';


import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
=
import { ChakraProvider } from '@chakra-ui/react';


import { AuthProvider } from '../components/AuthContext.jsx';
import theme from '../theme.tsx';
import '../styles/global.css';

export default function App({ Component, pageProps }) {
  return (
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </ChakraProvider>
  );
}
