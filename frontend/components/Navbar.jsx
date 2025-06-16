import Link from 'next/link';
import { useContext } from 'react';
import { AuthContext } from './AuthContext.jsx';

export default function Navbar() {
  const { token, logout } = useContext(AuthContext);
  return (
    <nav>
      <Link href="/">Home</Link>{' '}
      {token ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <Link href="/login">Login</Link>
      )}
    </nav>
  );
}

