import axios from 'axios';

import { computed, ref, onMounted } from 'vue';
import { defineStore } from 'pinia';
import { useRouter } from 'vue-router';

export const useUserStore = defineStore('user', () => {
  const router = useRouter();

  // State
  const isLoading = ref(false);
  const user = ref(null);
  // const token = ref(null);

  // Computed
  const isAuthenticated = computed(() => !!user.value);

  // Methods
  const setUser = (user) => {
    user.value = user;
  }
  const setSession = (token, user) => {
    if (token) {
      sessionStorage.setItem('token', token);
    } else {
      sessionStorage.removeItem('token');
    }
    // setToken(token);
    setUser(user);
  };
  const login = async (data) => {
    try {
      console.log('try', email, password);
      const response = await axios.post('/user/login/', data);
      console.log('response', response);
      if (response.status !== 200) {
        alert('Invalid email or password');
        return;
      }

      const { token, user } = response.data;

      if (token) {
        setSession(token, user);
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Error logging in:', error);
    }
  };
  const logout = async () => {
    const response = await axios.post('/user/logout/');

    if (response.status === 200) {
      setSession(null, null);
      router.push('/login');
    }
  };

  const signup = async (data) => {
    try {
      console.log('try', data.email, data.password);
      const response = await axios.post('/user/signup/', data);

      if (response.data.user.id) {
        alert('Sign up successful. Please log in');
        router.push('/login');
      }
    } catch (error) {
      alert(`Error - ${error.response?.data?.email[0]}` || 'An error occurred. Unable to sign up');
    }
  };
  const fetchUserData = async (token) => {
    try {
      const response = await axios.get('/user/whoami/');

      if (response.status === 200) {
        setSession(token);
        setUser(response.data);
      }

    } catch (error) {
      console.error('Error fetching user data:', error);
      setSession(null, null);
    }
  };
  const verifyStoredToken = async () => {
    const storedToken = sessionStorage.getItem('token');
    if (storedToken) {
      console.log('Stored token found:', storedToken);
      fetchUserData(storedToken);
    }
  };

  // Lifecycle hooks  
  onMounted(() => {
    verifyStoredToken();
  });

  return {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    signup,
  };
});