import Link from 'next/link';
import { useContext } from 'react';
<<<<<<< HEAD
=======
import { Flex, Button, IconButton, useColorMode } from '@chakra-ui/react';
import { SunIcon, MoonIcon } from '@chakra-ui/icons';
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
import { AuthContext } from './AuthContext.jsx';

export default function Navbar() {
  const { token, logout } = useContext(AuthContext);
<<<<<<< HEAD
  return (
    <nav>
      <Link href="/">Home</Link>{' '}
      {token ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <Link href="/login">Login</Link>
      )}
    </nav>
=======
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <Flex as="nav" p={4} mb={4} justify="space-between" align="center">
      <Link href="/">Home</Link>
      <div>
        <IconButton
          mr={2}
          aria-label="Toggle dark mode"
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          _focusVisible={{ boxShadow: 'outline' }}
        />
        {token ? (
          <Button onClick={logout} ml={2} aria-label="Logout" _focusVisible={{ boxShadow: 'outline' }}>
            Logout
          </Button>
        ) : (
          <Link href="/login">
            <Button ml={2} aria-label="Login" _focusVisible={{ boxShadow: 'outline' }}>
              Login
            </Button>
          </Link>
        )}
      </div>
    </Flex>
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
  );
}

