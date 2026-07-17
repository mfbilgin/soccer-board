import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Geliştirme aşaması için bilgisayarın IP'sini girmemiz gerekebilir (Emülatörler için)
// Fiziksel cihaz testi için bilgisayarın yerel ağ IP'sini (örn: 192.168.1.x) girmelisin.
// export const API_URL = "http://192.168.1.10:8000/api"; 

// --- CANLI ORTAM (PRODUCTION) AYARI ---
// APK Derlemeden (Build) önce aşağıdaki satırı aktif et ve kendi Droplet IP'ni yaz!
export const DROPLET_IP = "209.38.237.30"; // <-- Burayı değiştir
export const API_URL = `http://${DROPLET_IP}:8000/api`;


const api = axios.create({
  baseURL: API_URL,
  timeout: 5000, // 5 saniye zaman aşımı
});

// Her istekte token'ı otomatik ekle
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('userToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
