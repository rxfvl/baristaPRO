import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView, ActivityIndicator } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';
import BottomNavBar from '../components/BottomNavBar';

export default function AddExtractionScreen({ navigation }) {
  const { userToken } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  
  const [beans, setBeans] = useState([]);
  const [loadingBeans, setLoadingBeans] = useState(true);
  
  const [selectedBatchId, setSelectedBatchId] = useState('');
  
  const [dose, setDose] = useState('18.0');
  const [yieldAmount, setYieldAmount] = useState('36.0');
  const [time, setTime] = useState('25');
  const [waterTemp, setWaterTemp] = useState('93.0');
  const [grindSize, setGrindSize] = useState('');
  const [pressure, setPressure] = useState('9.0');
  const [preInfusion, setPreInfusion] = useState('0.0');
  
  const [acidity, setAcidity] = useState('5');
  const [sweetness, setSweetness] = useState('5');
  const [body, setBody] = useState('5');
  const [bitterness, setBitterness] = useState('5');
  const [score, setScore] = useState('7.0');
  
  const [flavorNotes, setFlavorNotes] = useState('');
  const [notes, setNotes] = useState('');
  
  const [saving, setSaving] = useState(false);
  const [advising, setAdvising] = useState(false);
  const [advisorResult, setAdvisorResult] = useState(null);

  const handleAdviseShot = async () => {
    setAdvising(true);
    setAdvisorResult(null);
    try {
      const response = await client.post('/extractions/advise', {
        dose_in: parseFloat(dose) || 18.0,
        yield_out: parseFloat(yieldAmount) || 36.0,
        extraction_time: parseFloat(time) || 25.0,
        water_temp: parseFloat(waterTemp) || 93.0,
        pressure: parseFloat(pressure) || 9.0,
        pre_infusion_time: parseFloat(preInfusion) || 0.0,
        acidity: parseInt(acidity) || 5,
        sweetness: parseInt(sweetness) || 5,
        body: parseInt(body) || 5,
        bitterness: parseInt(bitterness) || 5,
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      setAdvisorResult(response.data);
    } catch (e) {
      console.log('Error calling advisor', e);
      Alert.alert(t('error'), t('err_advise'));
    } finally {
      setAdvising(false);
    }
  };

  useEffect(() => {
    const fetchBeans = async () => {
      try {
        const response = await client.get('/beans/', {
          headers: { Authorization: `Bearer ${userToken}` }
        });
        setBeans(response.data);
        // Find the first bean with a batch to select by default
        for (let b of response.data) {
          if (b.batches && b.batches.length > 0) {
            setSelectedBatchId(b.batches[0].id.toString());
            break;
          }
        }
      } catch (e) {
        console.log('Error fetching beans', e);
      } finally {
        setLoadingBeans(false);
      }
    };
    fetchBeans();
  }, [userToken]);

  const handleSave = async () => {
    if (!selectedBatchId || !dose || !yieldAmount || !time) {
      Alert.alert(t('error'), t('err_req_ext'));
      return;
    }

    setSaving(true);
    try {
      await client.post('/extractions/', {
        bean_batch_id: parseInt(selectedBatchId),
        dose_in: parseFloat(dose),
        yield_out: parseFloat(yieldAmount),
        extraction_time: parseInt(time),
        water_temp: parseFloat(waterTemp) || 93.0,
        grind_size: grindSize || null,
        pressure: parseFloat(pressure) || 9.0,
        pre_infusion_time: parseFloat(preInfusion) || 0.0,
        acidity: parseInt(acidity) || 5,
        sweetness: parseInt(sweetness) || 5,
        body: parseInt(body) || 5,
        bitterness: parseInt(bitterness) || 5,
        score: parseFloat(score) || 7.0,
        flavor_notes: flavorNotes || null,
        notes: notes || null
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      
      Alert.alert(t('success'), t('success_ext_added'));
      // Navigation could go home, but staying and clearing is also fine
      navigation.navigate('Inicio');
    } catch (e) {
      console.log('Error saving extraction', e);
      Alert.alert(t('error'), t('err_saving_ext'));
    } finally {
      setSaving(false);
    }
  };

  if (loadingBeans) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  // Get flat list of batches
  const batches = [];
  beans.forEach(b => {
    if (b.batches && b.batches.length > 0) {
      b.batches.forEach(batch => {
        batches.push({
          batch_id: batch.id,
          roaster: b.roaster,
          name: b.name,
          roast_date: batch.roast_date
        });
      });
    }
  });

  return (
    <View style={styles.container}>
      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={{ paddingBottom: 40 }}>
        <Text style={styles.title}>{t('new_dialin')}</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('step_1')}</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.beansScroll}>
            {batches.map((b) => (
              <TouchableOpacity
                key={b.batch_id}
                style={[
                  styles.beanChip,
                  selectedBatchId === b.batch_id.toString() && styles.beanChipSelected
                ]}
                onPress={() => setSelectedBatchId(b.batch_id.toString())}
              >
                <Text style={[
                  styles.beanChipText,
                  selectedBatchId === b.batch_id.toString() && styles.beanChipTextSelected
                ]}>
                  {b.roaster} - {b.name} {b.roast_date ? `(${b.roast_date})` : ''}
                </Text>
              </TouchableOpacity>
            ))}
            {batches.length === 0 && (
              <Text style={styles.noBeansText}>{t('add_bean_first')}</Text>
            )}
          </ScrollView>

          <View style={styles.separator} />
          <Text style={styles.sectionTitle}>{t('step_2')}</Text>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('dose_in')}</Text>
              <TextInput style={styles.input} placeholder="18.0" placeholderTextColor={COLORS.textSecondary} value={dose} onChangeText={setDose} keyboardType="numeric" />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('yield_out')}</Text>
              <TextInput style={styles.input} placeholder="36.0" placeholderTextColor={COLORS.textSecondary} value={yieldAmount} onChangeText={setYieldAmount} keyboardType="numeric" />
            </View>
          </View>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('time_s')}</Text>
              <TextInput style={styles.input} placeholder="25" placeholderTextColor={COLORS.textSecondary} value={time} onChangeText={setTime} keyboardType="numeric" />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('grind_label')}</Text>
              <TextInput style={styles.input} placeholder="Ej: 14 clicks" placeholderTextColor={COLORS.textSecondary} value={grindSize} onChangeText={setGrindSize} />
            </View>
          </View>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('temp')}</Text>
              <TextInput style={styles.input} placeholder="93.0" placeholderTextColor={COLORS.textSecondary} value={waterTemp} onChangeText={setWaterTemp} keyboardType="numeric" />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('pressure')}</Text>
              <TextInput style={styles.input} placeholder="9.0" placeholderTextColor={COLORS.textSecondary} value={pressure} onChangeText={setPressure} keyboardType="numeric" />
            </View>
          </View>

          <View style={styles.separator} />
          <Text style={styles.sectionTitle}>{t('step_3')}</Text>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('acidity')}</Text>
              <TextInput style={styles.input} placeholder="5" placeholderTextColor={COLORS.textSecondary} value={acidity} onChangeText={setAcidity} keyboardType="numeric" />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('sweetness')}</Text>
              <TextInput style={styles.input} placeholder="5" placeholderTextColor={COLORS.textSecondary} value={sweetness} onChangeText={setSweetness} keyboardType="numeric" />
            </View>
          </View>
          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('body')}</Text>
              <TextInput style={styles.input} placeholder="5" placeholderTextColor={COLORS.textSecondary} value={body} onChangeText={setBody} keyboardType="numeric" />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>{t('bitterness')}</Text>
              <TextInput style={styles.input} placeholder="5" placeholderTextColor={COLORS.textSecondary} value={bitterness} onChangeText={setBitterness} keyboardType="numeric" />
            </View>
          </View>

          <Text style={styles.label}>{t('global_score')}</Text>
          <TextInput style={styles.input} placeholder="7.5" placeholderTextColor={COLORS.textSecondary} value={score} onChangeText={setScore} keyboardType="numeric" />

          <Text style={styles.label}>{t('flavor_notes')}</Text>
          <TextInput style={styles.input} placeholder="Chocolate oscuro, almendras..." placeholderTextColor={COLORS.textSecondary} value={flavorNotes} onChangeText={setFlavorNotes} />

          <Text style={styles.label}>{t('extra_notes')}</Text>
          <TextInput style={[styles.input, styles.textArea]} placeholder="Bajar medio punto la molienda..." placeholderTextColor={COLORS.textSecondary} value={notes} onChangeText={setNotes} multiline />

          <TouchableOpacity style={styles.aiButton} onPress={handleAdviseShot} disabled={advising}>
            {advising ? (
              <ActivityIndicator color={COLORS.primary} />
            ) : (
              <Text style={styles.aiButtonText}>{t('consult_advisor')}</Text>
            )}
          </TouchableOpacity>

          {advisorResult && (
            <View style={styles.advisorCard}>
              <Text style={styles.advisorTitle}>{t('advisor_title')}</Text>
              <Text style={styles.advisorText}>{advisorResult.diagnostic}</Text>
              {advisorResult.deltas && Object.keys(advisorResult.deltas).length > 0 && (
                <>
                  <Text style={styles.advisorSubtitle}>{t('advisor_sugg')}</Text>
                  {Object.entries(advisorResult.deltas).map(([key, value]) => (
                    <Text key={key} style={styles.advisorDelta}>
                      • {key}: {value > 0 ? `+${value}` : value}
                    </Text>
                  ))}
                  <Text style={styles.advisorScore}>{t('advisor_score')} {advisorResult.suggested_score}/10</Text>
                </>
              )}
            </View>
          )}

          <TouchableOpacity style={styles.button} onPress={handleSave} disabled={saving}>
            {saving ? (
              <ActivityIndicator color={COLORS.bgBase} />
            ) : (
              <Text style={styles.buttonText}>{t('save_extraction')}</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
      <BottomNavBar />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgBase,
    paddingTop: 50,
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.bgBase,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginHorizontal: SIZES.padding,
    marginBottom: 20,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    marginHorizontal: SIZES.padding,
    padding: 20,
    borderRadius: SIZES.radius,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginBottom: 15,
  },
  separator: {
    height: 1,
    backgroundColor: COLORS.bgInput,
    marginVertical: 20,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    width: '48%',
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
  textArea: {
    height: 80,
    textAlignVertical: 'top',
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
  beansScroll: {
    marginBottom: 20,
    flexGrow: 0,
  },
  beanChip: {
    backgroundColor: COLORS.bgBase,
    borderWidth: 1,
    borderColor: COLORS.bgInput,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 10,
  },
  beanChipSelected: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  beanChipText: {
    color: COLORS.textSecondary,
    fontSize: 14,
  },
  beanChipTextSelected: {
    color: COLORS.bgBase,
    fontWeight: 'bold',
  },
  noBeansText: {
    color: COLORS.danger,
    fontStyle: 'italic',
    paddingVertical: 10,
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
  advisorCard: {
    backgroundColor: COLORS.bgInput,
    padding: 16,
    borderRadius: SIZES.radius,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  advisorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginBottom: 10,
  },
  advisorText: {
    color: COLORS.textPrimary,
    marginBottom: 10,
    fontSize: 15,
  },
  advisorSubtitle: {
    fontWeight: 'bold',
    color: COLORS.primary,
    marginTop: 10,
    marginBottom: 5,
  },
  advisorDelta: {
    color: COLORS.textPrimary,
    marginLeft: 10,
  },
  advisorScore: {
    color: COLORS.primary,
    fontWeight: 'bold',
    marginTop: 10,
    fontStyle: 'italic',
  }
});
