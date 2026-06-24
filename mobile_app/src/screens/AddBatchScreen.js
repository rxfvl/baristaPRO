import React, { useState, useContext } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView, ActivityIndicator } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';

export default function AddBatchScreen({ route, navigation }) {
  const { userToken } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  
  // beanId and beanName passed from BeansScreen
  const { beanId, beanName } = route.params || {};
  
  const [roastDate, setRoastDate] = useState('');
  const [stockGrams, setStockGrams] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!beanId) {
      Alert.alert(t('error'), t('err_no_bean_sel'));
      return;
    }

    setSaving(true);
    try {
      await client.post('/batches/', {
        bean_id: beanId,
        roast_date: roastDate || null,
        stock_grams: stockGrams ? parseFloat(stockGrams) : 0,
        rest_days_min: 7,
        rest_days_max: 14
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      
      Alert.alert(t('success'), t('success_batch_added'));
      navigation.goBack();
    } catch (e) {
      console.log('Error saving batch', e);
      Alert.alert(t('error'), t('err_saving_batch'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backButtonText}>{t('back')}</Text>
          </TouchableOpacity>
          <Text style={styles.title}>{t('add_batch')}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.subtitle}>{t('bean_label')} <Text style={{color: COLORS.primary}}>{beanName}</Text></Text>

          <Text style={styles.label}>{t('roast_date_label')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: 2026-06-01"
            placeholderTextColor={COLORS.textSecondary}
            value={roastDate}
            onChangeText={setRoastDate}
          />

          <Text style={styles.label}>{t('initial_stock')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: 250"
            placeholderTextColor={COLORS.textSecondary}
            value={stockGrams}
            onChangeText={setStockGrams}
            keyboardType="numeric"
          />

          <TouchableOpacity style={styles.button} onPress={handleSave} disabled={saving}>
            {saving ? (
              <ActivityIndicator color={COLORS.bgBase} />
            ) : (
              <Text style={styles.buttonText}>{t('save_batch')}</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgBase,
    paddingTop: 50,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SIZES.padding,
    marginBottom: 20,
  },
  backButton: {
    marginRight: 15,
  },
  backButtonText: {
    color: COLORS.primary,
    fontSize: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  subtitle: {
    fontSize: 18,
    color: COLORS.textPrimary,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    marginHorizontal: SIZES.padding,
    padding: 20,
    borderRadius: SIZES.radius,
    marginBottom: 40,
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
  button: {
    backgroundColor: COLORS.primary,
    padding: 16,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: COLORS.bgBase,
    fontSize: 16,
    fontWeight: 'bold',
  },
});
