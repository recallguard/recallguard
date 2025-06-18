import Link from 'next/link';
import { useContext } from 'react';
import { useTranslation } from 'next-i18next';
import {
  Flex,
  Button,
  IconButton,
  useColorMode,
  HStack,
  Drawer,
  DrawerOverlay,
  DrawerContent,
  DrawerHeader,
  DrawerBody,
  useDisclosure,
  Spacer,
} from '@chakra-ui/react';
import { HamburgerIcon, SunIcon, MoonIcon } from '@chakra-ui/icons';
import { AuthContext } from './AuthContext.jsx';
import AlertsModal from './AlertsModal.jsx';
import LanguageSwitcher from './LanguageSwitcher.jsx';

export default function Navbar() {
  const { token, logout } = useContext(AuthContext);
  const { colorMode, toggleColorMode } = useColorMode();
  const { t } = useTranslation('common');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const MenuLinks = (
    <HStack spacing={4} align="center">
      <Link href="/">{t('home')}</Link>
      <Link href="/transparency">{t('transparency')}</Link>
      {token ? (
        <Button onClick={logout} aria-label="Logout" _focusVisible={{ boxShadow: 'outline' }}>
          {t('logout')}
        </Button>
      ) : (
        <Link href="/login">
          <Button aria-label="Login" _focusVisible={{ boxShadow: 'outline' }}>
            {t('login')}
          </Button>
        </Link>
      )}
      {token && <AlertsModal />}
      <LanguageSwitcher />
      <IconButton
        aria-label="Toggle dark mode"
        icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
        onClick={toggleColorMode}
        _focusVisible={{ boxShadow: 'outline' }}
      />
    </HStack>
  );

  return (
    <Flex as="header" position="sticky" top="0" zIndex="1000" px={4} py={2} boxShadow="sm" bg="chakra-body-bg">
      <HStack w="full" align="center">
        <IconButton
          display={{ base: 'inline-flex', md: 'none' }}
          aria-label="Open menu"
          icon={<HamburgerIcon />}
          onClick={onOpen}
        />
        <Link href="/">RecallGuard</Link>
        <Spacer />
        <HStack spacing={4} display={{ base: 'none', md: 'flex' }}>
          {MenuLinks}
        </HStack>
      </HStack>
      <Drawer placement="left" onClose={onClose} isOpen={isOpen}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerHeader>Menu</DrawerHeader>
          <DrawerBody>{MenuLinks}</DrawerBody>
        </DrawerContent>
      </Drawer>
    </Flex>
  );
}
