import React, { useContext, useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';
import BottomNavBar from '../components/BottomNavBar';
import { User, LogOut, Settings } from 'lucide-react-native';

export default function ProfileScreen({ navigation }) {
  const { user, userToken, logout, fetchUser } = useContext(AuthContext);
  const { language, changeLanguage, t } = useContext(LanguageContext);
  
  const [nickname, setNickname] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setNickname(user.nickname || '');
    }
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    try {
      // Update user nickname in backend
      await client.put('/users/me', {
        nickname: nickname || null
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      
      Alert.alert(t('success'), t('profile_saved'));
      // Refetch user context so other screens update immediately
      if (typeof fetchUser === 'function') {
        await fetchUser(userToken);
      }
    } catch (e) {
      console.log('Error saving profile', e);
      Alert.alert(t('error'), t('error_saving'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <Text style={styles.title}>{t('profile')}</Text>
        </View>

        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <User color={COLORS.primary} size={24} />
            <Text style={styles.sectionTitle}>{t('personal_data')}</Text>
          </View>
          
          <Text style={styles.label}>{t('email')}</Text>
          <TextInput
            style={[styles.input, styles.inputDisabled]}
            value={user?.email || ''}
            editable={false}
          />

          <Text style={styles.label}>{t('nickname')}</Text>
          <TextInput
            style={styles.input}
            placeholder={t('nickname_ph')}
            placeholderTextColor={COLORS.textSecondary}
            value={nickname}
            onChangeText={setNickname}
          />
        </View>

        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Settings color={COLORS.primary} size={24} />
            <Text style={styles.sectionTitle}>{t('preferences')}</Text>
          </View>
          
          <Text style={styles.label}>{t('app_lang')}</Text>
          <View style={styles.languageContainer}>
            <TouchableOpacity 
              style={[styles.langButton, language === 'es' && styles.langButtonActive]}
              onPress={() => changeLanguage('es')}
            >
              <Text style={[styles.langText, language === 'es' && styles.langTextActive]}>Español</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.langButton, language === 'en' && styles.langButtonActive]}
              onPress={() => changeLanguage('en')}
            >
              <Text style={[styles.langText, language === 'en' && styles.langTextActive]}>English</Text>
            </TouchableOpacity>
          </View>
        </View>

        <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={saving}>
          {saving ? (
            <ActivityIndicator color={COLORS.bgBase} />
          ) : (
            <Text style={styles.saveButtonText}>{t('save_changes')}</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity style={styles.logoutButtonFull} onPress={logout}>
          <LogOut color={COLORS.danger} size={20} />
          <Text style={styles.logoutTextFull}>{t('logout')}</Text>
        </TouchableOpacity>

      </ScrollView>
      <BottomNavBar />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgBase,
  },
  scrollContainer: {
    paddingTop: 50,
    paddingHorizontal: SIZES.padding,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    padding: 20,
    borderRadius: SIZES.radius,
    marginBottom: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginLeft: 10,
  },
  label: {
    color: COLORS.textSecondary,
    marginBottom: 8,
    fontSize: 14,
  },
  input: {
    backgroundColor: COLORS.bgInput,
    color: COLORS.textPrimary,
    borderRadius: SIZES.radius,
    padding: 12,
    marginBottom: 20,
    fontSize: 16,
  },
  inputDisabled: {
    color: COLORS.textSecondary,
    opacity: 0.7,
  },
  languageContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  langButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    backgroundColor: COLORS.bgInput,
    borderRadius: SIZES.radius,
    borderWidth: 1,
    borderColor: COLORS.bgInput,
    marginHorizontal: 5,
  },
  langButtonActive: {
    backgroundColor: COLORS.primary + '20', // 20% opacity
    borderColor: COLORS.primary,
  },
  langText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    fontWeight: 'bold',
  },
  langTextActive: {
    color: COLORS.primary,
  },
  saveButton: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 30,
  },
  saveButtonText: {
    color: COLORS.bgBase,
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButtonFull: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.danger,
    borderRadius: SIZES.radius,
    marginBottom: 20,
  },
  logoutTextFull: {
    color: COLORS.danger,
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  }
});
