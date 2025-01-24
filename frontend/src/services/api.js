const API_URL = 'http://localhost:8000';
const LLM_URL = 'http://localhost:8001';

const decodeToken = (token) => {
 try {
   const base64Url = token.split('.')[1];
   const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
   const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => 
     '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
   return JSON.parse(jsonPayload);
 } catch (error) {
   console.error('Error decoding token:', error);
   return null;
 }
};

export const loginUser = async (username, password) => {
 try {
   const formData = new FormData();
   formData.append('username', username);
   formData.append('password', password);

   const response = await fetch(`${API_URL}/auth/login`, {
     method: 'POST',
     body: formData,
   });

   if (!response.ok) {
     const errorData = await response.json().catch(() => null);
     throw new Error(errorData?.detail || 'Login failed');
   }

   const data = await response.json();
   const token = data.access_token;
   if (!token) throw new Error('No token received from server');

   const decoded = decodeToken(token);
   if (!decoded?.role) throw new Error('Invalid token format');

   localStorage.setItem('token', token);
   localStorage.setItem('userRole', decoded.role);

   return { token, role: decoded.role };
 } catch (error) {
   console.error('Login error:', error);
   throw error;
 }
};

export const registerUser = async (userData) => {
 try {
   const response = await fetch(`${API_URL}/auth/register`, {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(userData),
   });

   if (!response.ok) {
     const errorData = await response.json().catch(() => null);
     throw new Error(errorData?.detail || 'Registration failed');
   }
   return await response.json();
 } catch (error) {
   console.error('Registration error:', error);
   throw error;
 }
};

export const searchBusinesses = async (query) => {
 try {
   const response = await fetch(`${API_URL}/api/services/smart-service-search`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       ...getAuthHeader()
     },
     body: JSON.stringify({ query }),
   });

   if (!response.ok) throw new Error('Search failed');
   return await response.json();
 } catch (error) {
   console.error('Search error:', error);
   throw error;
 }
};

export const getAuthHeader = () => {
 const token = localStorage.getItem('token');
 return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const API_CONFIG = {
 BACKEND: API_URL,
 LLM_SERVICE: LLM_URL
};