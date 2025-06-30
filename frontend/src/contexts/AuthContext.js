import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Set up axios defaults
  axios.defaults.baseURL = 'http://localhost:8000';

  useEffect(() => {
    // Check for stored token on app load
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        const user = JSON.parse(userData);
        setUser(user);
        setIsAuthenticated(true);
        
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const getErrorMessage = (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      return 'Unable to connect to the server. Please check your connection and try again.';
    }
    
    if (error.response?.status === 500) {
      return 'Server error. Please try again later.';
    }
    
    if (error.response?.status === 401) {
      return 'Authentication failed. Please log in again.';
    }
    
    if (error.response?.status === 403) {
      return 'Access denied. Please check your permissions.';
    }
    
    if (error.response?.status === 404) {
      return 'Resource not found.';
    }
    
    return 'An unexpected error occurred. Please try again.';
  };

  const login = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/auth/login', formData);
      const { token, user_id, username: userUsername } = response.data;

      // Store token and user data
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify({ id: user_id, username: userUsername }));

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      setUser({ id: user_id, username: userUsername });
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: getErrorMessage(error)
      };
    }
  };

  const register = async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/auth/register', formData);
      const { token, user_id, username: userUsername } = response.data;

      // Store token and user data
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify({ id: user_id, username: userUsername }));

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      setUser({ id: user_id, username: userUsername });
      setIsAuthenticated(true);

      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: getErrorMessage(error)
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 