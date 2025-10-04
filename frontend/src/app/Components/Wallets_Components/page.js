import React from 'react';
import Dashboard from '../System_Management_Component/dashboard/dashboard';
import Sidebar from '../System_Management_Component/dashboard/SideBar/sidebar';
import Wallets from './Wallets';

export default function WalletsPage() {
  return (
    <div className="flex flex-row h-screen">
      <Sidebar />
      <div className="flex-1 p-8">
        <Wallets />
      </div>
    </div>
  );
}
