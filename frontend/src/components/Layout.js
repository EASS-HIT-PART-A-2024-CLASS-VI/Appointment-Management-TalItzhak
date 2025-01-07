import React from 'react';

const Layout = ({ children }) => {
 return (
   <div className="min-h-screen bg-gray-900 text-white relative">
     {children}
   </div>
 );
};

export default Layout;