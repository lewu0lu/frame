import {createWebHistory, createRouter} from 'vue-router'

import EmptyView from '@/content/Empty.vue'
import FileView from '@/content/FileManagement.vue'
import ScriptView from '@/content/ScriptManagement.vue'

import ScriptPanel from '@/panels/ScriptPanel.vue';
import ChainPanel from '@/panels/TaskChainPanel.vue';
import FilePanel from '@/panels/FileManagePanel.vue'
import RuntimePanel from "@/panels/RuntimePanel.vue";


import PackagePanel from '@/panels/PackagePanel.vue';
const routes = [
    {path: '/:pathMatch(.*)*', redirect: '/'},
    {path: '/', component: EmptyView},
    {
        path: '/file',
        component: FileView,
        children: [
            {path: 'manage', component: FilePanel},
        ]
    },
    {
        path: '/interface',
        component: ScriptView,
        children: [
            {path: 'manage', component: ScriptPanel},
            {path: 'chain', component: ChainPanel},
            {path: 'packages', component: PackagePanel},
            {path: 'runtime', component: RuntimePanel},
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router