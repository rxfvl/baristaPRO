import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/context/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import { LanguageProvider } from './src/context/LanguageContext';

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <LanguageProvider>
          <StatusBar style="light" />
          <AppNavigator />
        </LanguageProvider>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
