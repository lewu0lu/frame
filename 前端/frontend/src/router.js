import {createWebHistory, createRouter} from 'vue-router'
import { isAuthenticated } from '@/api/user_api';

import EmptyView from '@/content/Empty.vue'
import Dashboard from '@/content/Dashboard.vue'
import ScriptView from '@/content/ScriptManagement.vue'
import Login from '@/content/Login.vue'
import Register from '@/content/Register.vue'

import ScriptPanel from '@/panels/ScriptPanel.vue';
import ChainPanel from '@/panels/TaskChainPanel.vue';
import RuntimePanel from "@/panels/RuntimePanel.vue";
import PackagePanel from '@/panels/PackagePanel.vue';

const routes = [
    {path: '/', redirect: '/login'},
    {path: '/:pathMatch(.*)*', redirect: '/login'},
    {path: '/login', component: Login, meta: { guest: true }},
    {path: '/register', component: Register, meta: { guest: true }},
    {
        path: '/',
        component: Dashboard,
        meta: { requiresAuth: true },
        children: [
            {path: 'home', component: EmptyView},
            {
                path: 'interface',
                component: ScriptView,
                children: [
                    {path: 'manage', component: ScriptPanel},
                    {path: 'chain', component: ChainPanel},
                    {path: 'packages', component: PackagePanel},
                    {path: 'runtime', component: RuntimePanel},
                ]
            }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isGuestRoute = to.matched.some(record => record.meta.guest);
    const authenticated = isAuthenticated();
    
    if (requiresAuth && !authenticated) {
        // 需要登录但未登录，重定向到登录页
        next('/login');
    } else if (isGuestRoute && authenticated) {
        // 已登录用户访问登录/注册页，重定向到首页
        next('/home');
    } else if (to.path === '/' && authenticated) {
        // 已登录用户访问根路径，重定向到首页
        next('/home');
    } else {
        // 其他情况正常导航
        next();
    }
});

export default router
