import axios from 'axios';
import config from "./config.js";
// 创建一个 axios 实例，用于与脚本 API 通信
const script_api = axios.create({
    baseURL: config.scriptApiBaseUrl, // 设置基础 URL
    headers: {
        'Content-Type': 'application/json', // 设置默认请求头
    },
    timeout: 5000, // 设置请求超时时间为 5 秒
});

// 获取所有脚本url
export const getAllScriptInfo = async () => {
    try {
        const response = await script_api.get('/script_tree');
        return response.data; // 返回响应数据
    } catch (error) {
        throw error; // 抛出错误
    }
};

// 获取脚本的所有版本信息
export const getScriptAllVersion = async (data) => {
    try {
        const response = await script_api.post('/all_version', data);
        return response.data; // 返回响应数据
    } catch (error) {
        throw error; // 抛出错误
    }
};

// 获取脚本的当前版本信息
export const getScriptCurrentVersion = async (data) => {
    try {
        const response = await script_api.post('/script_info', data);
        return response.data; // 返回响应数据
    } catch (error) {
        throw error; // 抛出错误
    }
};

// 设置脚本版本
export const setScriptVersion = async (data) => {
    try {
        const response = await script_api.post('/set_version', data);
        return response.data; // 返回响应数据
    } catch (error) {
        throw error; // 抛出错误
    }
};

// 取消设置脚本版本
export const unsetScriptVersion = async (data) => {
    try {
        const response = await script_api.post('/cancel_set_version', data);
        return response.data; // 返回响应数据
    } catch (error) {
        throw error; // 抛出错误
    }
};

// 上传脚本
export const uploadScript = async (data, fileItem) => {
    const formData = new FormData();
    formData.append('file', fileItem);
    for (const key of Object.keys(data)) {
        formData.append(key, data[key]);
    }
    console.log(formData);
    try {
        const response = await script_api.post(
            '/upload_script',
            formData,
            {headers: {'Content-Type': 'multipart/form-data'}});
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 验证脚本参数
export const validateScriptParameters = async (scriptUrl, parameters = {}) => {
    try {
        const response = await script_api.post('/validate_parameters', {
            script_url: scriptUrl,
            parameters: parameters
        });
        
        return response.data;
    } catch (error) {
        console.error('验证脚本参数错误:', error);
        throw error;
    }
};

// 运行脚本
export const runScript = async (scriptUrl, parameters = {}, forceRun = false) => {
    try {
        console.log('运行脚本请求:', `${config.scriptApiBaseUrl}/run_script`, {script_url: scriptUrl, parameters, force_run: forceRun});
        
        const response = await script_api.post('/run_script', {
            script_url: scriptUrl,
            parameters: parameters,
            force_run: forceRun
        });
        
        console.log('运行脚本响应:', response.data);
        return response.data;
    } catch (error) {
        console.error('运行脚本错误:', error);
        throw error;
    }
};
