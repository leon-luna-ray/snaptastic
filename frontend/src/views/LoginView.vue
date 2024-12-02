<template>
    <div id="login" class="flex flex-col-2 justify-center items-center">
        <div class="flex flex-col gap-y-[2rem] bg-green-400 px-[6rem] py-[4rem] rounded-md">
            <h1 class="text-center text-[3rem]">Login</h1>
            <form @submit.prevent="userStore.login(formData)" class="flex flex-col gap-y-[1rem]">
                <div class="flex flex-col gap-y-[0.5rem]">
                    <label for="username">Email</label>
                    <input type="text" id="email" v-model="formData.email" class="border" />
                </div>
                <div class="flex flex-col gap-y-[0.5rem]">
                    <label for="password">Password</label>
                    <input type="password" id="password" v-model="formData.password" class="border" />
                </div>
                <button :class="['mt-[1rem] py-[0.75rem] border rounded-md hover:bg-green-300/40', loadingClass]" :disabled="isLoading" type="submit">{{ buttonText }}</button>
            </form>
        </div>
        <div class="signup-link text-[0.75rem]">
            <p>Don't have an account? <router-link to='/signup'>Click here to sign up!</router-link></p>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useUserStore } from '../stores/user'

// Store
const userStore = useUserStore();

// State
const { isLoading } = storeToRefs(userStore);
const formData = ref({
    email: '',
    password: '',
});

// Computed
const buttonText = computed(() => {
    return isLoading.value ? 'Loading...' : 'Login';
})
const loadingClass = computed(() => ({
    'hover:cursor-not-allowed bg-gray-400': isLoading.value,
}))
</script>
