/**
 * 前端工具函数库
 */

// API请求工具
const API = {
    /**
     * 获取认证 header
     */
    getAuthHeaders() {
        const token = localStorage.getItem('access_token');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    },

    /**
     * 发送GET请求
     */
    async get(url) {
        const response = await fetch(url, {
            headers: this.getAuthHeaders()
        });
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    },

    /**
     * 发送POST请求
     */
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        return await response.json();
    },

    /**
     * 发送DELETE请求
     */
    async delete(url) {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        });
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Delete failed');
        }
        return await response.json();
    }
};

// 文件大小格式化
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 日期格式化
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 显示加载状态
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
        element.classList.remove('hidden');
    }
}

// 隐藏加载状态
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

// 显示错误消息
function showError(message) {
    alert(message); // 可以改为更友好的toast提示
}

// 显示成功消息
function showSuccess(message) {
    alert(message); // 可以改为更友好的toast提示
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 检查用户是否已登录
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// 退出登录
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}
