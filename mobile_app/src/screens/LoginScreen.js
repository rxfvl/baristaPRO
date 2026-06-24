import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import { COLORS, SIZES } from '../theme/colors';

export default function LoginScreen() {
  const { login } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert(t('error'), t('login_err_empty'));
      return;
    }
    
    setLoading(true);
    try {
      await login(email, password);
    } catch (e) {
      Alert.alert(t('error'), t('login_err_cred'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <View style={styles.card}>
        <Text style={styles.title}>BaristaPRO</Text>
        <Text style={styles.subtitle}>{t('login_subtitle')}</Text>

        <TextInput
          style={styles.input}
          placeholder={t('email')}
          placeholderTextColor={COLORS.textSecondary}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />

        <TextInput
          style={styles.input}
          placeholder={t('password')}
          placeholderTextColor={COLORS.textSecondary}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity 
          style={styles.button} 
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={COLORS.bgBase} />
          ) : (
            <Text style={styles.buttonText}>{t('enter')}</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgBase,
    justifyContent: 'center',
    padding: SIZES.padding,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    padding: 24,
    borderRadius: SIZES.radius,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.primary,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: 32,
  },
  input: {
    backgroundColor: COLORS.bgInput,
    color: COLORS.textPrimary,
    borderRadius: SIZES.radius,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  button: {
    backgroundColor: COLORS.primary,
    borderRadius: SIZES.radius,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: COLORS.bgBase,
    fontSize: 18,
    fontWeight: 'bold',
  },
});
