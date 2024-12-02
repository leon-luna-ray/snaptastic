import axios from 'axios';

const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;

axios.defaults.baseURL = BASE_API_URL;

axios.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axios;
