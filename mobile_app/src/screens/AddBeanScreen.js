import React, { useState, useContext } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView, ActivityIndicator } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';

export default function AddBeanScreen({ navigation }) {
  const { userToken } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  
  const [roaster, setRoaster] = useState('');
  const [name, setName] = useState('');
  const [originCountry, setOriginCountry] = useState('');
  const [originRegion, setOriginRegion] = useState('');
  const [originFarm, setOriginFarm] = useState('');
  const [variety, setVariety] = useState('');
  const [process, setProcess] = useState('');
  const [altitude, setAltitude] = useState('');
  const [notes, setNotes] = useState('');
  // Flavor Predictor state
  const [expectedAcidity, setExpectedAcidity] = useState(null);
  const [expectedSweetness, setExpectedSweetness] = useState(null);
  const [expectedBody, setExpectedBody] = useState(null);
  const [expectedBitterness, setExpectedBitterness] = useState(null);
  const [predicting, setPredicting] = useState(false);
  
  // Create a batch automatically
  const [roastDate, setRoastDate] = useState('');
  const [stockGrams, setStockGrams] = useState('');
  
  const [saving, setSaving] = useState(false);

  const handlePredictFlavor = async () => {
    setPredicting(true);
    try {
      const response = await client.post('/beans/predict_flavor', {
        variety: variety || "Unknown",
        process: process || "Unknown",
        origin_country: originCountry || "Unknown",
        altitude_masl: altitude ? parseFloat(altitude) : 1200.0,
        days_since_roast: 14.0,
        notes: notes || ""
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      
      const { acidity, sweetness, body, bitterness } = response.data;
      setExpectedAcidity(acidity.toString());
      setExpectedSweetness(sweetness.toString());
      setExpectedBody(body.toString());
      setExpectedBitterness(bitterness.toString());
      
      Alert.alert(t('predict_done_title'), t('predict_done_msg'));
    } catch (e) {
      console.log('Error predicting flavor', e);
      Alert.alert(t('error'), t('predict_err_msg'));
    } finally {
      setPredicting(false);
    }
  };

  const handleSave = async () => {
    if (!roaster || !name) {
      Alert.alert(t('error'), t('err_req_roaster_name'));
      return;
    }

    setSaving(true);
    try {
      const response = await client.post('/beans/', {
        roaster,
        name,
        origin_country: originCountry || null,
        origin_region: originRegion || null,
        origin_farm: originFarm || null,
        variety: variety || null,
        process: process || null,
        altitude_masl: altitude ? parseInt(altitude) : null,
        notes: notes || null,
        expected_acidity: expectedAcidity ? parseFloat(expectedAcidity) : null,
        expected_sweetness: expectedSweetness ? parseFloat(expectedSweetness) : null,
        expected_body: expectedBody ? parseFloat(expectedBody) : null,
        expected_bitterness: expectedBitterness ? parseFloat(expectedBitterness) : null,
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      
      const newBean = response.data;
      
      // Auto-create batch if needed
      if (stockGrams || roastDate) {
        await client.post('/batches/', {
          bean_id: newBean.id,
          roast_date: roastDate || null,
          stock_grams: stockGrams ? parseFloat(stockGrams) : 0,
          rest_days_min: 7,
          rest_days_max: 14
        }, {
          headers: { Authorization: `Bearer ${userToken}` }
        });
      }
      
      Alert.alert(t('success'), t('success_bean_added'));
      navigation.goBack();
    } catch (e) {
      console.log('Error saving bean', e);
      Alert.alert(t('error'), t('err_saving_bean'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingBottom: 40 }}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backButtonText}>{t('back')}</Text>
          </TouchableOpacity>
          <Text style={styles.title}>{t('new_bean')}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>{t('roaster')} *</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Nomad Coffee"
            placeholderTextColor={COLORS.textSecondary}
            value={roaster}
            onChangeText={setRoaster}
          />

          <Text style={styles.label}>{t('coffee_name')} *</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Finca San José"
            placeholderTextColor={COLORS.textSecondary}
            value={name}
            onChangeText={setName}
          />

          <Text style={styles.label}>{t('origin_country')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Colombia"
            placeholderTextColor={COLORS.textSecondary}
            value={originCountry}
            onChangeText={setOriginCountry}
          />

          <Text style={styles.label}>{t('region')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Huila"
            placeholderTextColor={COLORS.textSecondary}
            value={originRegion}
            onChangeText={setOriginRegion}
          />

          <Text style={styles.label}>{t('farm')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Pedro Pérez"
            placeholderTextColor={COLORS.textSecondary}
            value={originFarm}
            onChangeText={setOriginFarm}
          />

          <Text style={styles.label}>{t('variety')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Caturra, Gesha..."
            placeholderTextColor={COLORS.textSecondary}
            value={variety}
            onChangeText={setVariety}
          />

          <Text style={styles.label}>{t('process')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: Lavado, Natural..."
            placeholderTextColor={COLORS.textSecondary}
            value={process}
            onChangeText={setProcess}
          />

          <Text style={styles.label}>{t('altitude')}</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: 1800"
            placeholderTextColor={COLORS.textSecondary}
            value={altitude}
            onChangeText={setAltitude}
            keyboardType="numeric"
          />
          
          <TouchableOpacity style={styles.aiButton} onPress={handlePredictFlavor} disabled={predicting}>
            {predicting ? (
              <ActivityIndicator color={COLORS.primary} />
            ) : (
              <Text style={styles.aiButtonText}>{t('predict_flavor')}</Text>
            )}
          </TouchableOpacity>

          {(expectedAcidity !== null || expectedSweetness !== null) && (
            <View style={styles.aiResultContainer}>
              <Text style={styles.sectionTitle}>{t('sensory_expected')}</Text>
              <View style={styles.row}>
                <View style={styles.halfInput}>
                  <Text style={styles.label}>{t('acidity')}</Text>
                  <TextInput style={styles.input} value={expectedAcidity} onChangeText={setExpectedAcidity} keyboardType="numeric" />
                </View>
                <View style={styles.halfInput}>
                  <Text style={styles.label}>{t('sweetness')}</Text>
                  <TextInput style={styles.input} value={expectedSweetness} onChangeText={setExpectedSweetness} keyboardType="numeric" />
                </View>
              </View>
              <View style={styles.row}>
                <View style={styles.halfInput}>
                  <Text style={styles.label}>{t('body')}</Text>
                  <TextInput style={styles.input} value={expectedBody} onChangeText={setExpectedBody} keyboardType="numeric" />
                </View>
                <View style={styles.halfInput}>
                  <Text style={styles.label}>{t('bitterness')}</Text>
                  <TextInput style={styles.input} value={expectedBitterness} onChangeText={setExpectedBitterness} keyboardType="numeric" />
                </View>
              </View>
            </View>
          )}

          <Text style={styles.label}>{t('notes_flavors')}</Text>
          <TextInput
            style={[styles.input, { height: 60, textAlignVertical: 'top' }]}
            placeholder="Chocolate, Caramelo, Manzana..."
            placeholderTextColor={COLORS.textSecondary}
            value={notes}
            onChangeText={setNotes}
            multiline
          />

          <View style={styles.separator} />
          <Text style={styles.sectionTitle}>{t('first_batch')}</Text>

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
              <Text style={styles.buttonText}>{t('save_bean')}</Text>
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
  separator: {
    height: 1,
    backgroundColor: COLORS.bgInput,
    marginVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: 15,
  },
  aiButton: {
    backgroundColor: COLORS.bgInput,
    padding: 16,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    marginVertical: 15,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  aiButtonText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: 'bold',
  },
  aiResultContainer: {
    backgroundColor: COLORS.bgInput,
    padding: 16,
    borderRadius: SIZES.radius,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    width: '48%',
  }
});
