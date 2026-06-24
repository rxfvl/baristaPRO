import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://79.72.62.76:8000/api';

const client = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Add a request interceptor to inject the JWT token
client.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default client;
