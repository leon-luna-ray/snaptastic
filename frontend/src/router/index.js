import { createRouter, createWebHistory } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores/user';
const routes = [
  {
    path: '/',
    component: () => import('@/views/HomeView.vue'),
    name: 'Home',
  },
  {
    path: '/login',
    component: () => import('@/views/LoginView.vue'),
    name: 'Login',
  },
  {
    path: '/signup',
    component: () => import('@/views/SignupView.vue'),
    name: 'Signup',
  },
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardView.vue'),
    name: 'Dashboard',
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// todo fix route guard
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();
  const { token } = storeToRefs(userStore);
  
   userStore.verifySession();

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token.value) {
      next({ name: 'Login' });
    } else {
      next();
    }
  } else {
    next();
  }
});


export default router;
