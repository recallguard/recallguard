import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  fonts: {
    heading: `'Inter', system-ui, sans-serif`,
    body: `'Inter', system-ui, sans-serif`,
  },
  colors: {
    brand: {
      50: '#f5faff',
      100: '#e0f2ff',
      500: '#1e88e5',
      700: '#1565c0',
    },
  },
  fontWeights: {
    normal: 400,
    medium: 600,
    bold: 700,
  },
  components: {
    Button: {
      baseStyle: { borderRadius: 'md' },
    },
    Table: {
      baseStyle: {
        th: { fontWeight: 'medium' },
      },
    },
  },
});

export default theme;
