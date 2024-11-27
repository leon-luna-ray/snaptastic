import axios from 'axios';
import { ref } from 'vue';
import { defineStore } from 'pinia';

const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;

const axiosInstance = axios.create({
    baseURL: BASE_API_URL,
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const useRecipeStore = defineStore('recipe', () => {
    
    const userRecipes = ref([]);
    
    const fetchRecipes = async () => {
        try {
            const response = await axiosInstance.get('/recipes');
            userRecipes.value = response.data;
        } catch (error) {
            console.error('Failed to fetch recipes:', error);
        }
    };

    return {
        fetchRecipes,
    };
});