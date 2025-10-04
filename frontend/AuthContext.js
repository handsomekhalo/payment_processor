'use client'; // This directive is correct for Client Components

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  // Initialize authToken and csrfToken to null initially.
  // We will load them from localStorage in a useEffect.
  const [authToken, setAuthToken] = useState(null);
  const [csrfToken, setCSRFToken] = useState(null);
  // isLoading is crucial here to prevent rendering children until tokens are loaded from localStorage
  const [isLoading, setIsLoading] = useState(true); // Start as true

  const router = useRouter();

  // This useEffect will run *only on the client side* after initial render
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken');
      const csrf = localStorage.getItem('csrfToken');

      // Update state only if tokens are found and valid (not 'null' string)
      if (token && token !== 'null') {
        setAuthToken(token);
      }
      if (csrf && csrf !== 'null') {
        setCSRFToken(csrf);
      }
    }
    setIsLoading(false); // Once localStorage check is done, set isLoading to false
  }, []); // Run only once on client-side mount

  const login = (token, csrf) => {
    const actualToken = token && token !== 'null' ? token : null;
    const actualCsrf = csrf && csrf !== 'null' ? csrf : null;

    setAuthToken(actualToken);
    setCSRFToken(actualCsrf);
    localStorage.setItem('authToken', actualToken || '');
    localStorage.setItem('csrfToken', actualCsrf || '');
  };

  const logout = () => {
    setAuthToken(null);
    setCSRFToken(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('csrfToken');
    localStorage.removeItem('user');
    router.push('/');
  };

  const navigate = (path) => {
    router.push(path);
  };

  const isAuthenticated = !!authToken;

  const contextValue = {
    authToken,
    csrfToken,
    isAuthenticated,
    isLoading, // Provide isLoading to consumers
    login,
    logout,
    navigate,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {/* Only render children when we know whether they are authenticated or not.
          This prevents rendering content that requires authentication (or redirection)
          before the token from localStorage has been read on the client. */}
      {!isLoading && children}
    </AuthContext.Provider>
  );
};