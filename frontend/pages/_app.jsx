import { ChakraProvider } from '@chakra-ui/react';
import { AuthProvider } from '../components/AuthContext.jsx';
import '../styles/global.css';

export default function App({ Component, pageProps }) {
  return (
    <ChakraProvider>
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </ChakraProvider>
  );
}
