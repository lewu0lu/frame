import axios from 'axios';
import config from "./config.js";

// 创建一个 axios 实例，用于与任务链 API 通信
const chain_api = axios.create({
    baseURL: config.chainApiBaseUrl, // 设置基础 URL
    headers: {
        'Content-Type': 'application/json', // 设置请求头
    },
    timeout: 5000, // 设置请求超时时间为 5 秒
});

// 获取所有任务链信息
export const getAllChainInfo = async () => {
    try {
        const response = await chain_api.get('/get_task_chain');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 获取任务信息
export const getChainNodesInfo = async (data) => {
    try {
        const response = await chain_api.post('/get_task_info', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 设置任务链
export const uploadTaskChain = async (data) => {
    try {
        const response = await chain_api.post('/set_task_chain', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 重置任务链
export const resetTaskChain = async (data) => {
    try {
        const response = await chain_api.post('/reset_task_chain', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 删除任务链
export const deleteTaskChain = async (data) => {
    try {
        const response = await chain_api.post('/delete_task_chain', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 获取所有请求记录
export const getAllOperatingRecord = async () => {
    try {
        const response = await chain_api.get('/request_list');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 获取任务信息和日志
export const getOperatingRecord = async (data) => {
    try {
        const response = await chain_api.post('/get_task_log', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 停止运行中的任务链
export const stopOperatingChain = async (data) => {
    try {
        const response = await chain_api.post('/stop_task', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};
