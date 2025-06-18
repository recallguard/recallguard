import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'recentRecalls';

export async function saveRecalls(arr: any[]) {
  try {
    const existing = await loadRecalls();
    const combined = [...arr, ...existing].slice(0, 50);
    await AsyncStorage.setItem(KEY, JSON.stringify(combined));
  } catch {}
}

export async function loadRecalls(): Promise<any[]> {
  try {
    const str = await AsyncStorage.getItem(KEY);
    return str ? JSON.parse(str) : [];
  } catch {
    return [];
  }
}
