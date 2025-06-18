import { useEffect, useState } from 'react';
import { View, Text, FlatList, RefreshControl } from 'react-native';
import { loadRecalls } from '../utils/cache';

export default function Dashboard() {
  const [recalls, setRecalls] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    const data = await loadRecalls();
    setRecalls(data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <FlatList
      data={recalls}
      keyExtractor={(_, i) => i.toString()}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={async () => {
            setRefreshing(true);
            await load();
            setRefreshing(false);
          }}
        />
      }
      renderItem={({ item }) => (
        <View style={{ padding: 8, borderBottomWidth: 1 }}>
          <Text>{item.product}</Text>
          <Text>{item.status}</Text>
        </View>
      )}
    />
  );
}
