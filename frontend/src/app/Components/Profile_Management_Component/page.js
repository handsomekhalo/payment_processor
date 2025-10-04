import React from 'react';
import Sidebar from '../System_Management_Component/dashboard/SideBar/sidebar';
import Wallets from '../Wallets_Components/Wallets';
import ManageProfileModal from './ManageProfileModal';

export default function ProfilePage() {
  return (
    <div className="flex flex-row h-screen">
      <Sidebar />
      <div className="flex-1 p-8">
        <ManageProfileModal />
      </div>
    </div>
  );
}
