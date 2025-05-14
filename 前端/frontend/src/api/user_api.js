import config from './config';
const apiBaseUrl = config.apiBaseUrl;

/**
 * 用户注册
 * @param {Object} userData - 用户数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @returns {Promise<Object>} - 注册结果
 */
export async function register(userData) {
  try {
    console.log('注册请求:', `${apiBaseUrl}/user/register`, userData);
    
    const response = await fetch(`${apiBaseUrl}/user/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(userData),
      mode: 'cors',
      credentials: 'same-origin'
    });
    
    console.log('注册响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      if (response.status === 0) {
        throw new Error('网络错误，请检查后端服务是否运行');
      }
      
      let errorData;
      try {
        errorData = await response.json();
        console.error('注册错误数据:', errorData);
      } catch (e) {
        console.error('解析错误响应失败:', e);
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }
      
      throw new Error(errorData.message || '注册失败');
    }
    
    const data = await response.json();
    console.log('注册成功数据:', data);
    
    // 保存令牌到本地存储
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  } catch (error) {
    console.error('注册错误:', error);
    throw error;
  }
}

/**
 * 用户登录
 * @param {Object} credentials - 登录凭证
 * @param {string} credentials.username - 用户名
 * @param {string} credentials.password - 密码
 * @returns {Promise<Object>} - 登录结果
 */
export async function login(credentials) {
  try {
    console.log('登录请求:', `${apiBaseUrl}/user/login`, credentials);
    
    const response = await fetch(`${apiBaseUrl}/user/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(credentials),
      mode: 'cors',
      credentials: 'same-origin'
    });
    
    console.log('登录响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      if (response.status === 0) {
        throw new Error('网络错误，请检查后端服务是否运行');
      }
      
      let errorData;
      try {
        errorData = await response.json();
        console.error('登录错误数据:', errorData);
      } catch (e) {
        console.error('解析错误响应失败:', e);
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }
      
      throw new Error(errorData.message || '登录失败');
    }
    
    const data = await response.json();
    console.log('登录成功数据:', data);
    
    // 保存令牌到本地存储
    if (data.token) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  } catch (error) {
    console.error('登录错误:', error);
    throw error;
  }
}

/**
 * 验证令牌
 * @returns {Promise<Object>} - 验证结果
 */
export async function verifyToken() {
  try {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('未找到令牌');
    }
    
    console.log('验证令牌请求:', `${apiBaseUrl}/user/verify-token`);
    
    const response = await fetch(`${apiBaseUrl}/user/verify-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ token }),
      mode: 'cors',
      credentials: 'same-origin'
    });
    
    console.log('验证令牌响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      if (response.status === 0) {
        throw new Error('网络错误，请检查后端服务是否运行');
      }
      
      let errorData;
      try {
        errorData = await response.json();
        console.error('验证令牌错误数据:', errorData);
      } catch (e) {
        console.error('解析错误响应失败:', e);
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }
      
      throw new Error(errorData.message || '令牌验证失败');
    }
    
    const data = await response.json();
    console.log('验证令牌成功数据:', data);
    
    // 更新用户信息
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  } catch (error) {
    console.error('令牌验证错误:', error);
    // 清除无效的令牌和用户信息
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    throw error;
  }
}

/**
 * 获取用户信息
 * @returns {Promise<Object>} - 用户信息
 */
export async function getUserProfile() {
  try {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('未找到令牌');
    }
    
    console.log('获取用户信息请求:', `${apiBaseUrl}/user/profile`);
    
    const response = await fetch(`${apiBaseUrl}/user/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      mode: 'cors',
      credentials: 'same-origin'
    });
    
    console.log('获取用户信息响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      if (response.status === 0) {
        throw new Error('网络错误，请检查后端服务是否运行');
      }
      
      let errorData;
      try {
        errorData = await response.json();
        console.error('获取用户信息错误数据:', errorData);
      } catch (e) {
        console.error('解析错误响应失败:', e);
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }
      
      throw new Error(errorData.message || '获取用户信息失败');
    }
    
    const data = await response.json();
    console.log('获取用户信息成功数据:', data);
    
    // 更新用户信息
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  } catch (error) {
    console.error('获取用户信息错误:', error);
    throw error;
  }
}

/**
 * 用户登出
 */
export function logout() {
  // 清除本地存储中的令牌和用户信息
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

/**
 * 获取当前用户
 * @returns {Object|null} - 当前用户信息或null
 */
export function getCurrentUser() {
  const userJson = localStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
}

/**
 * 检查用户是否已登录
 * @returns {boolean} - 是否已登录
 */
export function isAuthenticated() {
  return !!localStorage.getItem('token');
}
