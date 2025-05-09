import axios from 'axios';
import config from './config.js';
// 创建用于与文件API通信的axios实例
const file_api = axios.create({
    baseURL: config.fileApiBaseUrl,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 5000,
});

// 创建用于与S3存储通信的axios实例
const s3_api = axios.create({
    baseURL: config.s3ApiBaseUrl,
    headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': config.s3AuthorizationToken,
    },
    timeout: 5000,
});

// 获取文件列表
export const getAllFileInfo = async () => {
    try {
        const response = await file_api.get('/file_list');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 获取文件版本信息
export const getFileVersionInfo = async (data) => {
    try {
        const response = await file_api.post('/file_version', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 检查文件是否存在
export const checkFileInfo = async (data) => {
    try {
        const response = await file_api.post('/find', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 上传文件
export const uploadFileInfo = async (data) => {
    try {
        const response = await file_api.post('/upload', data);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 将图片上传到S3存储
export const postImage2S3 = async (file_path, fileName, fileItem) => {
    const url = "/file_management/testing" + file_path + fileName;
    const formData = new FormData();
    formData.append('file', fileItem, fileName);
    try {
        const response = await s3_api.put(url, formData);
        return response.config.baseURL + response.config.url;
    } catch (error) {
        throw error;
    }
};
