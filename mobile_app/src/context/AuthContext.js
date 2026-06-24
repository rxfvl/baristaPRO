import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import client from '../api/client';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await client.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const token = response.data.access_token;
      setUserToken(token);
      await AsyncStorage.setItem('userToken', token);
      await fetchUser(token);
    } catch (e) {
      console.log('Login error', e);
      throw e;
    }
  };

  const fetchUser = async (token) => {
    try {
      const response = await client.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (e) {
      console.log('Fetch user error', e);
      logout();
    }
  };

  const logout = async () => {
    setUserToken(null);
    setUser(null);
    await AsyncStorage.removeItem('userToken');
  };

  const isLoggedIn = async () => {
    try {
      setIsLoading(true);
      let token = await AsyncStorage.getItem('userToken');
      setUserToken(token);
      if (token) {
        await fetchUser(token);
      }
      setIsLoading(false);
    } catch (e) {
      console.log('isLoggedIn error', e);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    isLoggedIn();
  }, []);

  return (
    <AuthContext.Provider value={{ login, logout, isLoading, userToken, user, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};
