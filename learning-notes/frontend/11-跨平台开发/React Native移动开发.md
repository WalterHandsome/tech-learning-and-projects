# React Native 移动开发

> Author: Walter Wang

## 1. 核心组件

```jsx
import { View, Text, Image, ScrollView, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello React Native</Text>
      <Image source={{ uri: 'https://example.com/image.jpg' }} style={styles.image} />
      <TouchableOpacity style={styles.button} onPress={() => alert('Pressed')}>
        <Text style={styles.buttonText}>点击我</Text>
      </TouchableOpacity>
    </View>
  );
}

// 样式（类似 CSS 的 Flexbox，但默认 flexDirection: 'column'）
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  image: { width: 200, height: 200, borderRadius: 8 },
  button: { backgroundColor: '#3498db', padding: 12, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontSize: 16 },
});
```

## 2. FlatList（高性能列表）

```jsx
<FlatList
  data={items}
  keyExtractor={(item) => item.id.toString()}
  renderItem={({ item }) => <ListItem item={item} />}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
  refreshing={refreshing}
  onRefresh={handleRefresh}
  ListEmptyComponent={<Text>暂无数据</Text>}
/>
```

## 3. 导航（React Navigation）

```jsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// 导航操作
function HomeScreen({ navigation }) {
  return (
    <Button title="详情" onPress={() => navigation.navigate('Detail', { id: 1 })} />
  );
}

function DetailScreen({ route }) {
  const { id } = route.params;
}
```

## 4. Expo

```bash
# 快速创建项目
npx create-expo-app my-app
npx expo start

# Expo 优势：
# - 无需配置原生环境
# - 丰富的内置 API（相机、位置、通知等）
# - OTA 更新
# - Expo Go 即时预览
```
