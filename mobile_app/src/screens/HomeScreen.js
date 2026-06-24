import React, { useContext, useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { LanguageContext } from '../context/LanguageContext';
import client from '../api/client';
import { COLORS, SIZES } from '../theme/colors';
import { Coffee, Droplet, PlusCircle } from 'lucide-react-native';
import BottomNavBar from '../components/BottomNavBar';

export default function HomeScreen({ navigation }) {
  const { user, userToken, logout } = useContext(AuthContext);
  const { t } = useContext(LanguageContext);
  const [beanCount, setBeanCount] = useState(0);
  const [extractionCount, setExtractionCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const beansRes = await client.get('/beans/', { headers: { Authorization: `Bearer ${userToken}` }});
        const extRes = await client.get('/extractions/', { headers: { Authorization: `Bearer ${userToken}` }});
        setBeanCount(beansRes.data.length);
        setExtractionCount(extRes.data.length);
      } catch (e) {
        console.log('Error fetching stats', e);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.header}>
          <Text>
            <Text style={styles.greeting}>{t('hello')} </Text>
            <Text style={styles.name}>{user?.nickname || user?.email?.split('@')[0] || 'Barista'}!</Text>
          </Text>
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Coffee color={COLORS.primary} size={32} />
            {loading ? <ActivityIndicator color={COLORS.primary} /> : <Text style={styles.statNumber}>{beanCount}</Text>}
            <Text style={styles.statLabel}>{t('stats_beans')}</Text>
          </View>
          <View style={styles.statCard}>
            <Droplet color={COLORS.primary} size={32} />
            {loading ? <ActivityIndicator color={COLORS.primary} /> : <Text style={styles.statNumber}>{extractionCount}</Text>}
            <Text style={styles.statLabel}>{t('stats_extractions')}</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>{t('quick_actions')}</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate('Dial-In')}>
          <PlusCircle color={COLORS.bgBase} size={24} />
          <Text style={styles.actionButtonText}>{t('new_dialin')}</Text>
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
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  name: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  logoutButton: {
    padding: 8,
  },
  logoutText: {
    color: COLORS.danger,
    fontSize: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 40,
  },
  statCard: {
    backgroundColor: COLORS.bgCard,
    borderRadius: SIZES.radius,
    padding: 20,
    alignItems: 'center',
    width: '48%',
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginTop: 10,
  },
  statLabel: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginTop: 5,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 15,
  },
  actionButton: {
    backgroundColor: COLORS.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: SIZES.radius,
  },
  actionButtonText: {
    color: COLORS.bgBase,
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
