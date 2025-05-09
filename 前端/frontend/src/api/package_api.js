import axios from 'axios';
import config from './config.js';
const package_api = axios.create({
    baseURL: config.packageApiBaseUrl,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 60000,
});

// 获取所有安装包列表
export const getAllPackageInfo = async () => {
    try {
        const response = await package_api.get('/package_list');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 安装包
export const installPackage = async (data) => {
    try{
        const response = await package_api.post('/install', data);
        return response.data;
    }catch(error){
        throw error;
    }
};

// 卸载包
export const uninstall = async (data) => {
    try{
        const response = await package_api.post('/uninstall', data);
        return response.data;
    }catch(error){
        throw error;
    }
};