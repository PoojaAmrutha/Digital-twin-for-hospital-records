// ============================================================================
// FILE: frontend/src/services/api.js
// API Service for Backend Communication
// ============================================================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // ========================================================================
  // User Endpoints
  // ========================================================================

  async createUser(userData) {
    return this.request('/users/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async getAllUsers() {
    return this.request('/users/');
  }

  // ========================================================================
  // Vitals Endpoints
  // ========================================================================

  async submitVitals(vitalsData) {
    return this.request('/vitals/', {
      method: 'POST',
      body: JSON.stringify(vitalsData),
    });
  }

  async getLatestVitals(userId) {
    return this.request(`/vitals/user/${userId}/latest`);
  }

  async getVitalsHistory(userId, limit = 100) {
    return this.request(`/vitals/user/${userId}/history?limit=${limit}`);
  }

  // ========================================================================
  // Alerts Endpoints
  // ========================================================================

  async getUserAlerts(userId, limit = 10) {
    return this.request(`/alerts/user/${userId}?limit=${limit}`);
  }

  async markAlertRead(alertId) {
    return this.request(`/alerts/${alertId}/mark-read`, {
      method: 'PUT',
    });
  }

  // ========================================================================
  // Health Score Endpoints
  // ========================================================================

  async getHealthScore(userId) {
    return this.request(`/health-score/user/${userId}`);
  }

  async getHealthScoreHistory(userId, limit = 30) {
    return this.request(`/health-score/user/${userId}/history?limit=${limit}`);
  }

  // ========================================================================
  // Hospital Dashboard Endpoints
  // ========================================================================

  async getAllPatients() {
    return this.request('/hospital/patients');
  }

  async getPatientDetails(userId) {
    return this.request(`/hospital/patient/${userId}/details`);
  }

  // ========================================================================
  // Statistics Endpoints
  // ========================================================================

  async getSystemStats() {
    return this.request('/stats/overview');
  }

  // ========================================================================
  // WebSocket Connection
  // ========================================================================

  connectWebSocket(userId, onMessage, onError) {
    const wsURL = this.baseURL.replace('http', 'ws');
    const ws = new WebSocket(`${wsURL}/ws/${userId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }
}

// Export singleton instance
const apiService = new APIService(API_BASE_URL);
export default apiService;


// ============================================================================
// FILE: frontend/src/utils/helpers.js
// Utility Helper Functions
// ============================================================================

// Format date and time
export const formatDateTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Format time only
export const formatTime = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

// Format date only
export const formatDate = (date) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
};

// Get health score color
export const getHealthScoreColor = (score) => {
  if (score >= 80) return 'text-green-600';
  if (score >= 60) return 'text-yellow-600';
  return 'text-red-600';
};

// Get health score background color
export const getHealthScoreBgColor = (score) => {
  if (score >= 80) return 'bg-green-100';
  if (score >= 60) return 'bg-yellow-100';
  return 'bg-red-100';
};

// Get risk level color
export const getRiskLevelColor = (riskLevel) => {
  switch (riskLevel) {
    case 'low':
      return 'text-green-600 bg-green-100';
    case 'medium':
      return 'text-yellow-600 bg-yellow-100';
    case 'high':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

// Get vital status (normal, warning, danger)
export const getVitalStatus = (vital, value) => {
  switch (vital) {
    case 'heart_rate':
      if (value < 40 || value > 130) return 'danger';
      if (value < 60 || value > 100) return 'warning';
      return 'normal';
    
    case 'spo2':
      if (value < 88) return 'danger';
      if (value < 95) return 'warning';
      return 'normal';
    
    case 'temperature':
      if (value > 38.5 || value < 35) return 'danger';
      if (value > 37.5 || value < 36) return 'warning';
      return 'normal';
    
    case 'stress':
      if (value > 4) return 'danger';
      if (value > 3) return 'warning';
      return 'normal';
    
    default:
      return 'normal';
  }
};

// Get vital status color
export const getVitalStatusColor = (status) => {
  switch (status) {
    case 'danger':
      return 'text-red-600 bg-red-100';
    case 'warning':
      return 'text-yellow-600 bg-yellow-100';
    case 'normal':
      return 'text-green-600 bg-green-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

// Format number with commas
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return num.toLocaleString('en-US');
};

// Round number to decimals
export const roundNumber = (num, decimals = 1) => {
  if (num === null || num === undefined) return 0;
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
};

// Calculate percentage
export const calculatePercentage = (value, total) => {
  if (!total) return 0;
  return Math.round((value / total) * 100);
};

// Get alert priority (for sorting)
export const getAlertPriority = (type) => {
  const priorities = {
    critical: 1,
    danger: 2,
    warning: 3,
    info: 4,
  };
  return priorities[type] || 5;
};

// Sort alerts by priority and time
export const sortAlerts = (alerts) => {
  return [...alerts].sort((a, b) => {
    const priorityDiff = getAlertPriority(a.type) - getAlertPriority(b.type);
    if (priorityDiff !== 0) return priorityDiff;
    
    // If same priority, sort by time (newest first)
    return new Date(b.timestamp) - new Date(a.timestamp);
  });
};

// Check if value is in normal range
export const isInNormalRange = (vital, value) => {
  const ranges = {
    heart_rate: { min: 60, max: 100 },
    spo2: { min: 95, max: 100 },
    temperature: { min: 36.1, max: 37.2 },
    stress: { min: 0, max: 2 },
  };
  
  const range = ranges[vital];
  if (!range) return true;
  
  return value >= range.min && value <= range.max;
};

// Generate random ID
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Debounce function
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Local storage helpers
export const storage = {
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return false;
    }
  },
  
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      return false;
    }
  },
};

// Validate email
export const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

// Validate phone number
export const isValidPhone = (phone) => {
  const re = /^\+?[\d\s-()]+$/;
  return re.test(phone);
};

// Get time ago string
export const getTimeAgo = (date) => {
  const seconds = Math.floor((new Date() - new Date(date)) / 1000);
  
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + ' years ago';
  
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + ' months ago';
  
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + ' days ago';
  
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + ' hours ago';
  
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + ' minutes ago';
  
  return Math.floor(seconds) + ' seconds ago';
};

// Export all helpers as default
export default {
  formatDateTime,
  formatTime,
  formatDate,
  getHealthScoreColor,
  getHealthScoreBgColor,
  getRiskLevelColor,
  getVitalStatus,
  getVitalStatusColor,
  formatNumber,
  roundNumber,
  calculatePercentage,
  getAlertPriority,
  sortAlerts,
  isInNormalRange,
  generateId,
  debounce,
  throttle,
  storage,
  isValidEmail,
  isValidPhone,
  getTimeAgo,
};