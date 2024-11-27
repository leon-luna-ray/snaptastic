<template>
    <header class="flex items-center py-[2rem]">
        <div class="container flex justify-between">
            <router-link to="/">Sanptastic</router-link>
            <nav>
                <div class="account">
                    <router-link v-if="user?.email" to="/dashboard">{{ user.email }}</router-link>
                    <div v-if="user?.email || isAuthenticated" @click="userStore.logout">Logout</div>
                    <router-link v-else-if="route.path !== '/login'" to="/login">Login</router-link>
                </div>
            </nav>
        </div>
    </header>
</template>

<script setup>
import { storeToRefs } from 'pinia';
import { useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';

const route = useRoute();
const userStore = useUserStore();

// State
const { isAuthenticated, user } = storeToRefs(userStore);
</script>