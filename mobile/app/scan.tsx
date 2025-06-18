import { BarCodeScanner } from 'expo-barcode-scanner';
import { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import { checkCode } from '@recallhero/shared/lib/scan-core';
import { saveRecalls } from '../utils/cache';

export default function Scan() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    BarCodeScanner.requestPermissionsAsync().then(({ status }) =>
      setHasPermission(status === 'granted')
    );
  }, []);

  const handleScan = ({ data }: { data: string }) => {
    checkCode(data)
      .then((r) => {
        setResult(r);
        saveRecalls([r]);
      })
      .catch(() => {});
  };

  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={{ flex: 1 }}>
      {hasPermission && (
        <BarCodeScanner onBarCodeScanned={handleScan} style={{ flex: 1 }} />
      )}
      {result && (
        <Text style={{ padding: 8 }}>
          {result.status === 'recalled' ? '⚠️ Recalled' : '✅ Safe'}
        </Text>
      )}
    </View>
  );
}
