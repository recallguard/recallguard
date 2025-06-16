<<<<<<< HEAD
import { AuthProvider } from '../components/AuthContext.jsx';

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
=======
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
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
  );
}
