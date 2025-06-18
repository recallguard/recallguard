import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { appWithTranslation } from 'next-i18next';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { AuthProvider } from '../components/AuthContext.jsx';
import theme from '../theme.tsx';
import '../styles/global.css';

function MyApp({ Component, pageProps }) {
  const router = useRouter();
  useEffect(() => {
    if (typeof navigator !== 'undefined') {
      const navLang = navigator.language.startsWith('es') ? 'es' : 'en';
      if (router.locale !== navLang) {
        router.replace(router.asPath, router.asPath, { locale: navLang });
      }
    }
  }, []);
  return (
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </ChakraProvider>
  );
}

export default appWithTranslation(MyApp);
