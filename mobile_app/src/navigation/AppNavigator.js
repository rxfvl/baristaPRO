import React, { useContext } from 'react';
import { NavigationContainer, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';

import { AuthContext } from '../context/AuthContext';
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import BeansScreen from '../screens/BeansScreen';
import AddExtractionScreen from '../screens/AddExtractionScreen';
import AddBeanScreen from '../screens/AddBeanScreen';
import AddBatchScreen from '../screens/AddBatchScreen';
import ProfileScreen from '../screens/ProfileScreen';
import { COLORS } from '../theme/colors';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
  const { isLoading, userToken } = useContext(AuthContext);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.bgBase }}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer theme={{
      ...DarkTheme,
      colors: {
        ...DarkTheme.colors,
        background: COLORS.bgBase,
        card: COLORS.bgCard,
        text: COLORS.textPrimary,
      }
    }}>
      <Stack.Navigator screenOptions={{ headerShown: false, animation: 'none' }}>
        {userToken == null ? (
          <Stack.Screen name="Login" component={LoginScreen} />
        ) : (
          <>
            <Stack.Screen name="Inicio" component={HomeScreen} />
            <Stack.Screen name="Granos" component={BeansScreen} />
            <Stack.Screen name="Dial-In" component={AddExtractionScreen} />
            <Stack.Screen name="AddBean" component={AddBeanScreen} />
            <Stack.Screen name="AddBatch" component={AddBatchScreen} />
            <Stack.Screen name="Perfil" component={ProfileScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
