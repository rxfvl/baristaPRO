import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity, RefreshControl } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';
import { Coffee, Plus } from 'lucide-react-native';
import BottomNavBar from '../components/BottomNavBar';

export default function BeansScreen({ navigation }) {
  const { userToken } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  const [beans, setBeans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchBeans = async () => {
    try {
      const response = await client.get('/beans/', {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      setBeans(response.data);
    } catch (e) {
      console.log('Error fetching beans', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      fetchBeans();
    });
    return unsubscribe;
  }, [navigation, userToken]);

  const [predictingId, setPredictingId] = useState(null);
  const [predictions, setPredictions] = useState({});

  const handlePredictFlavor = async (item) => {
    setPredictingId(item.id);
    try {
      const response = await client.post('/beans/predict_flavor', {
        bean_id: item.id
      }, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      setPredictions(prev => ({ ...prev, [item.id]: response.data }));
    } catch (e) {
      console.log('Error predicting flavor', e);
    } finally {
      setPredictingId(null);
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
          <Coffee color={COLORS.primary} size={24} />
          <View style={styles.cardTitleContainer}>
            <Text style={styles.roaster}>{item.roaster}</Text>
            <Text style={styles.beanName}>{item.name}</Text>
          </View>
        </View>
        <TouchableOpacity 
          style={styles.addBatchSmallBtn}
          onPress={() => navigation.navigate('AddBatch', { beanId: item.id, beanName: item.name })}
        >
          <Text style={styles.addBatchSmallText}>{t('add_batch_short')}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.detailsContainer}>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>{t('origin')}</Text>
          <Text style={styles.detailValue}>{item.origin_country || t('unknown')}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>{t('process')}</Text>
          <Text style={styles.detailValue}>{item.process || t('na')}</Text>
        </View>
      </View>

      <TouchableOpacity 
        style={styles.aiButton} 
        onPress={() => handlePredictFlavor(item)}
        disabled={predictingId === item.id}
      >
        {predictingId === item.id ? (
          <ActivityIndicator color={COLORS.bgBase} size="small" />
        ) : (
          <Text style={styles.aiButtonText}>{t('predict_flavor')}</Text>
        )}
      </TouchableOpacity>

      {predictions[item.id] && (
        <View style={styles.aiResultContainer}>
          <Text style={styles.aiResultTitle}>{t('sensory_expected')}</Text>
          <View style={styles.row}>
            <Text style={styles.aiResultText}>{t('acidity')}: {predictions[item.id].acidity}/10</Text>
            <Text style={styles.aiResultText}>{t('sweetness')}: {predictions[item.id].sweetness}/10</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.aiResultText}>{t('body')}: {predictions[item.id].body}/10</Text>
            <Text style={styles.aiResultText}>{t('bitterness')}: {predictions[item.id].bitterness}/10</Text>
          </View>
          <Text style={styles.aiConfidence}>
            {t('confidence')}: {predictions[item.id].confidence === 'high' ? t('high') : t('low')}
          </Text>
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>{t('my_beans')}</Text>
        <TouchableOpacity 
          style={styles.addButton} 
          onPress={() => navigation.navigate('AddBean')}
        >
          <Plus color={COLORS.bgBase} size={20} />
          <Text style={styles.addButtonText}>{t('new')}</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color={COLORS.primary} style={{ marginTop: 50 }} />
      ) : (
        <FlatList
          data={beans}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                fetchBeans();
              }}
              tintColor={COLORS.primary}
            />
          }
          ListEmptyComponent={
            <Text style={styles.emptyText}>{t('no_beans')}</Text>
          }
        />
      )}
      <BottomNavBar />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgBase,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: SIZES.padding,
    paddingBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },
  addButtonText: {
    color: COLORS.bgBase,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    paddingHorizontal: SIZES.padding,
    paddingBottom: 20,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    padding: 16,
    borderRadius: SIZES.radius,
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitleContainer: {
    marginLeft: 12,
  },
  roaster: {
    color: COLORS.textSecondary,
    fontSize: 14,
    textTransform: 'uppercase',
  },
  beanName: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: 'bold',
  },
  detailsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: COLORS.bgInput,
    paddingTop: 12,
  },
  detailItem: {
    flex: 1,
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 14,
    color: COLORS.textPrimary,
    fontWeight: '500',
  },
  addBatchSmallBtn: {
    backgroundColor: COLORS.bgInput,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: SIZES.radius,
    justifyContent: 'center',
    alignItems: 'center',
  },
  addBatchSmallText: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: 'bold',
  },
  emptyText: {
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: 40,
    fontSize: 16,
  },
  aiButton: {
    backgroundColor: COLORS.bgInput,
    padding: 12,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    marginTop: 15,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  aiButtonText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: 'bold',
  },
  aiResultContainer: {
    backgroundColor: COLORS.bgInput,
    padding: 16,
    borderRadius: SIZES.radius,
    marginTop: 15,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  aiResultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: COLORS.primary,
    marginBottom: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  aiResultText: {
    color: COLORS.textPrimary,
    fontSize: 14,
  },
  aiConfidence: {
    color: COLORS.textSecondary,
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 10,
  }
});
