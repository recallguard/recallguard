import * as Notifications from 'expo-notifications';
import { useEffect } from 'react';

export default function usePushToken() {
  useEffect(() => {
    Notifications.getExpoPushTokenAsync().then((res) => {
      const token = res.data;
      if (token) {
        fetch(`/api/push/${encodeURIComponent(token)}`, { method: 'POST' }).catch(
          () => {}
        );
      }
    });
  }, []);
}
