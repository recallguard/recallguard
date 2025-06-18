import { Menu, MenuButton, MenuList, MenuItem, Button } from '@chakra-ui/react';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';

export default function LanguageSwitcher() {
  const router = useRouter();
  const { t } = useTranslation('common');
  const { locale, asPath } = router;
  const change = (lng) => {
    router.push(asPath, asPath, { locale: lng });
  };
  return (
    <Menu>
      <MenuButton as={Button}>{locale.toUpperCase()}</MenuButton>
      <MenuList>
        <MenuItem onClick={() => change('en')}>EN</MenuItem>
        <MenuItem onClick={() => change('es')}>ES</MenuItem>
      </MenuList>
    </Menu>
  );
}
