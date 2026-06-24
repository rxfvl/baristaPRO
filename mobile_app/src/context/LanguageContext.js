import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LABELS } from '../utils/translations';

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState('es');

  useEffect(() => {
    const loadLang = async () => {
      try {
        const savedLang = await AsyncStorage.getItem('userLang');
        if (savedLang) {
          setLanguageState(savedLang);
        }
      } catch (e) {
        console.log('Failed to load language from storage', e);
      }
    };
    loadLang();
  }, []);

  const changeLanguage = async (lang) => {
    try {
      setLanguageState(lang);
      await AsyncStorage.setItem('userLang', lang);
    } catch (e) {
      console.log('Failed to save language to storage', e);
    }
  };

  const t = (key) => {
    if (!LABELS[key]) {
      return key; // Fallback to key itself if missing
    }
    return LABELS[key][language] || LABELS[key]['es'] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};
