'use client';

import { useAuth } from '../../../../../AuthContext';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from './SideBar/navheader';
import Sidebar from './SideBar/sidebar';

export default function Dashboard() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/Components/System_Management_Component/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <p className="text-center mt-10 text-gray-600">Checking authentication...</p>;
  }

  if (!isAuthenticated) {
    return null; // Or show a loading spinner
  }


  return (
        <div>
          <Navbar />
          <Sidebar/>
          
          {/* Your dashboard content here */}
        </div>
  )
}

