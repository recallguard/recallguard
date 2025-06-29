import React from 'react';

import { useTranslation } from 'next-i18next';

export default function Index() {
  const { t } = useTranslation('common');
  return <div>{t('welcome')}</div>;
}
