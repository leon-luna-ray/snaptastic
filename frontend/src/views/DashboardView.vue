<template>
    <div class="flex justify-center items-center">
        <h1>User Dashboard</h1>
        <button @click="userStore.logout">Logout</button>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
</script>