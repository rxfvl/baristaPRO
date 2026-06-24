import React, { useContext } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Home, Coffee, PlusCircle, User } from 'lucide-react-native';
import { COLORS } from '../theme/colors';
import { LanguageContext } from '../context/LanguageContext';

export default function BottomNavBar() {
  const navigation = useNavigation();
  const route = useRoute();

  const { t } = useContext(LanguageContext);

  const tabs = [
    { name: t('nav_home'), icon: Home, routeName: 'Inicio' },
    { name: t('nav_beans'), icon: Coffee, routeName: 'Granos' },
    { name: t('nav_dialin'), icon: PlusCircle, routeName: 'Dial-In' },
    { name: t('nav_profile'), icon: User, routeName: 'Perfil' },
  ];

  return (
    <View style={styles.container}>
      {tabs.map((tab) => {
        const isActive = route.name === tab.routeName;
        const IconComponent = tab.icon;
        return (
          <TouchableOpacity 
            key={tab.routeName} 
            style={styles.tab} 
            onPress={() => navigation.navigate(tab.routeName)}
          >
            <IconComponent 
              color={isActive ? COLORS.primary : COLORS.textSecondary} 
              size={24} 
            />
            <Text style={[styles.text, { color: isActive ? COLORS.primary : COLORS.textSecondary }]}>
              {tab.name}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: COLORS.bgCard,
    borderTopWidth: 1,
    borderTopColor: COLORS.bgInput,
    paddingBottom: 20, // For safe area on iOS
    paddingTop: 10,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontSize: 12,
    marginTop: 4,
  }
});
