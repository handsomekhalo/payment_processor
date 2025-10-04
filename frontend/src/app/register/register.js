'use client';

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../../AuthContext';
import backendApi from '../../../utils/backendApi';

const RegisterPage = () => {
  const { login: authLogin, navigateTo } = useAuth();
  const [csrfToken, setCsrfToken] = useState('');
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiStatus, setApiStatus] = useState({ status: 'idle', message: '' });

  // Fetch CSRF Token on Component Mount with better error handling
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        setApiStatus({ status: 'loading', message: 'Connecting to API...' });
        const response = await backendApi.get('/system_management/csrf/', { withCredentials: true });
        
        if (response.data && response.data.csrfToken) {
          setCsrfToken(response.data.csrfToken);
          setApiStatus({ status: 'success', message: 'Connected to API' });
        } else {
          setApiStatus({ status: 'error', message: 'Invalid response from API' });
        }
      } catch (error) {
        console.error('CSRF Token Fetch Error:', error);
        
        // Provide more helpful error messages
        if (error.message === 'Network Error') {
          setApiStatus({ 
            status: 'error', 
            message: 'Cannot connect to API server. Please check if the server is running and CORS is properly configured.' 
          });
        } else {
          setApiStatus({ 
            status: 'error', 
            message: `API Error: ${error.response?.data?.message || error.message}`
          });
        }
      }
    };
    
    fetchCsrfToken();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsSubmitting(true);

    // CSRF token fallback from cookies (if state is empty)
    const csrfFromCookies = document.cookie
      .split('; ')
      .find((row) => row.startsWith('csrftoken='))
      ?.split('=')[1];

    const tokenToUse = csrfToken || csrfFromCookies;

    if (!tokenToUse) {
      setErrors((prev) => ({ ...prev, csrf: 'CSRF token is missing. Please refresh and try again.' }));
      setIsSubmitting(false);
      return;
    }

    // Check if passwords match
    if (form.password !== form.confirm_password) {
      setErrors((prev) => ({ ...prev, password: 'Passwords do not match' }));
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await backendApi.post(
        '/system_management/register_user/',
        {
          first_name: form.first_name,
          last_name: form.last_name,
          email: form.email,
          phone_number: form.phone_number,
          password: form.password,
          confirm_password: form.confirm_password,
        },
        {
          headers: {
            'X-CSRFToken': tokenToUse,
            'Content-Type': 'application/json',
          },
          withCredentials: true,
        }
      );

      if (response.data.status === 'success') {
        const parsedData = response.data.data;
        const { token, user } = parsedData;

        if (token) {
          authLogin(token, tokenToUse);
          localStorage.setItem('user', JSON.stringify(user));
          navigateTo('/login');
        } else {
          setErrors((prev) => ({ ...prev, server: 'Registration failed. No token received.' }));
        }
      } else {
        setErrors((prev) => ({ ...prev, server: response.data.message || 'Registration failed. Please try again.' }));
      }
    } catch (err) {
      console.error('Registration error:', err);
      if (err.message === 'Network Error') {
        setErrors((prev) => ({ 
          ...prev, 
          server: 'Cannot connect to server. Please check your internet connection or contact support.'
        }));
      } else {
        setErrors((prev) => ({ 
          ...prev, 
          server: err.response?.data?.message || 'An error occurred. Please try again.'
        }));
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 className="text-center text-2xl font-bold text-gray-900">Create your account</h2>
        
        {/* API Status Indicator */}
        {apiStatus.status === 'error' && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            <p className="font-medium">API Connection Error</p>
            <p className="text-sm">{apiStatus.message}</p>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 mt-6 sm:mx-auto sm:w-full sm:max-w-sm">
        {/* Form fields remain the same */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">First Name</label>
            <input
              id="first_name"
              type="text"
              value={form.first_name}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">Last Name</label>
            <input
              id="last_name"
              type="text"
              value={form.last_name}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email Address</label>
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div>
          <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700">Phone Number</label>
          <input
            id="phone_number"
            type="tel"
            maxLength={10}
            pattern="[0-9]{10,11}"
            value={form.phone_number}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div className="relative">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={form.password}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <div
            className="absolute inset-y-0 right-3 top-[38px] flex items-center cursor-pointer"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </div>
        </div>

        <div className="relative">
          <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">Confirm Password</label>
          <input
            id="confirm_password"
            type={showConfirmPassword ? 'text' : 'password'}
            value={form.confirm_password}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <div
            className="absolute inset-y-0 right-3 top-[38px] flex items-center cursor-pointer"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting || apiStatus.status === 'error'}
          className={`w-full mt-4 ${
            isSubmitting || apiStatus.status === 'error' 
              ? 'bg-gray-400' 
              : 'bg-indigo-600 hover:bg-indigo-500'
          } text-white font-medium py-2 px-4 rounded-md`}
        >
          {isSubmitting ? 'Registering...' : 'Register'}
        </button>

        {/* Show errors if any */}
        {Object.keys(errors).length > 0 && (
          <div className="mt-4 text-red-500">
            {Object.values(errors).map((error, index) => (
              <p key={index}>{error}</p>
            ))}
          </div>
        )}
      </form>
    </div>
  );
};

export default RegisterPage;