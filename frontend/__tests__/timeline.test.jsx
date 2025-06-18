import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

jest.mock('next/router', () => ({ useRouter: () => ({ query: { id: '1' } }) }));

import RecallDetail from '../pages/recall/[id].jsx';
import { AuthContext } from '../components/AuthContext.jsx';

test('timeline snapshot', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    json: async () => ({
      product: 'Widget',
      hazard: 'Fire',
      remedy_updates: [
        { time: '2024-01-01', text: 'Initial' },
        { time: '2024-02-01', text: 'Follow-up' }
      ]
    })
  });
  const { asFragment, findByText } = render(
    <AuthContext.Provider value={{ token: 't' }}>
      <RecallDetail />
    </AuthContext.Provider>
  );
  await findByText('Widget');
  expect(asFragment()).toMatchSnapshot();
});
