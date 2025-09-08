'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../dashboard/SideBar/sidebar';
import UserTable from './usermanagement';
import { useAuth } from '../../../../../AuthContext';
import Navbar from '../dashboard/SideBar/navheader';
import backendApi from '../../../../../utils/backendApi';
import EditUserModal from './edit_user_modalr';
import CreateUserModal from './Create_User_Modal';
import DeleteUserModal from './delete_user_modal';


const UserManagement = () => {
//   const { authToken, isAuthenticated, navigate } = useAuth();
//   const { authToken, isAuthenticated, navigate, isLoading } = useAuth();

  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [csrfToken, setCsrfToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const usersPerPage = 6;
  const [selectedUser, setSelectedUser] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
const [userToDelete, setUserToDelete] = useState(null);
const [deleting, setDeleting] = useState(false);


  // Fetch CSRF Token
// In UserManagement.js
const { authToken, isAuthenticated, navigate, isLoading } = useAuth();

// Main data fetching effect
useEffect(() => {
  if (isLoading) {
    console.log('AuthContext still loading...');
    return;
  }

  if (!authToken || !isAuthenticated) {
    console.log('Not authenticated, redirecting to login');
    console.log('Auth state:', { authToken, isAuthenticated });
    navigate('/login');
    return;
  }

  console.log('Starting data fetch with auth token:', authToken);
  // Rest of your code...
}, [authToken, isAuthenticated, navigate, isLoading]);;

  // Fetch Users
  const fetchUsers = async () => {
    try {
      console.log('Fetching users with token:', authToken);
      const res = await backendApi.get('/system_management/get_all_users/', {
        headers: { Authorization: `Token ${authToken}` }
        
      });
      
      // Check if response data is a string or already an object
      let userData;
      if (typeof res.data === 'string') {
        try {
          userData = JSON.parse(res.data);
        } catch (parseErr) {
          console.error('Error parsing user data:', parseErr);
          throw new Error('Invalid user data format');
        }
      } else {
        userData = res.data;
      }
      
      console.log('Users data received:', userData);
      setUsers(userData.users || []);
      return true;
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError('Error loading users');
      return false;
    }
  };

  // Fetch Roles

  const fetchRoles = async () => {
    try {
      console.log('Fetching roles with token:', authToken);
      const res = await backendApi.get('/system_management/get_roles/', {
        headers: { Authorization: `Token ${authToken}` }
      });
  
      console.log('Roles data received:', res.data);
      // setRoles(res.data.roles || []); // FIXED: was user_types
      setRoles(res.data?.data?.roles || []);

      return true;
    } catch (err) {
      console.error('Failed to fetch roles:', err);
      setError(prev => prev || 'Error loading roles');
      return false;
    }
  };

  const handleEditClick = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };
  
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };
  

  const handleSaveUser = async (userId, formData) => {
    try {
      // Make sure role is always a valid integer or an empty string
      // Use a default value (like 1) if needed, or retain as empty string 
      // depending on your backend validation requirements
      let user_type_id = formData.role ? parseInt(formData.role) : "";
      
      // If parsing results in NaN, set to empty string or a default value
      if (isNaN(user_type_id)) {
        user_type_id = "";  // or set to a default role ID like 1
      }
      
      const payload = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        user_type_id: user_type_id,
      };
      
      console.log('Sending payload to backend:', payload);
      
      const response = await backendApi.post(
        `/system_management/update_user/${userId}/`, 
        payload,
        {
          headers: { 
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Update response:', response);
      
      if (response.data.status === 'success') {
        // Refresh user list after successful update
        await fetchUsers();
        handleCloseModal();
      } else {
        throw new Error(response.data.message || 'Failed to update user');
      }
    } catch (err) {
      console.error('Error updating user:', err);
      alert('Failed to update user: ' + (err.message || 'Unknown error'));
    }
  };

  // Main data fetching effect
  useEffect(() => {
    if (!authToken || !isAuthenticated) {
      console.log('Not authenticated, redirecting to login');
      navigate('/login');
      return;
    }

    
    const fetchData = async () => {
      setLoading(true);
      const usersSuccess = await fetchUsers();
      const rolesSuccess = await fetchRoles();
      setLoading(false);
      
      if (!usersSuccess || !rolesSuccess) {
        console.error('Data fetching incomplete');
      }
    };

    fetchData();
  }, [authToken, isAuthenticated, navigate]);

const handleCreateUser = async (formData) => {
  try {
    console.log('Creating user with data:', formData);
    
    const response = await backendApi.post(
        `/system_management/create_user/`, 
        formData,
      {
        headers: { 
          'Authorization': `Token ${authToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Create response:', response);
    
    if (response.data.status === 'success') {
      // Refresh user list after successful creation
      await fetchUsers();
      setIsCreateModalOpen(false);
      alert('User created successfully! Login credentials sent via email.');
    } else {
      throw new Error(response.data.message || 'Failed to create user');
    }
  } catch (err) {
    console.error('Error creating user:', err);
    alert('Failed to create user: ' + (err.response?.data?.message || err.message || 'Unknown error'));
  }
};

const handleDeleteClick = (user) => {
  setUserToDelete(user);
  setIsDeleteModalOpen(true);
};

const handleConfirmDelete = async (email) => {
  if (!email) {
    console.error('No email provided for deletion');
    return;
  }

  try {
    setDeleting(true);
    const response = await backendApi.post(
      '/system_management/delete_user/',
      { email },
      {
        headers: {
          Authorization: `Token ${authToken}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.data.status === 'success') {
      await fetchUsers();
      setIsDeleteModalOpen(false);
      setUserToDelete(null);
    } else {
      throw new Error(response.data.message || 'Delete failed');
    }
  } catch (error) {
    console.error('Delete error:', error);
    alert('Failed to delete user: ' + (error.response?.data?.message || error.message));
  } finally {
    setDeleting(false);
  }
};



const handleDelete = (user) => {
    console.log('Setting user to delete:', user);

  setUserToDelete(user); // assuming this state exists
  setIsDeleteModalOpen(true);
};
  // Pagination
  const indexOfLastUser = currentPage * usersPerPage;
  const indexOfFirstUser = indexOfLastUser - usersPerPage;
  const currentUsers = users.slice(indexOfFirstUser, indexOfLastUser);
  const totalPages = Math.ceil(users.length / usersPerPage);

  return (
    
    <div className="flex">
        
      <Sidebar />
      <div className="flex-1 p-4">
        <h2 className="text-2xl font-semibold mb-4">User Management</h2>
<button 
        type="button" 
        onClick={() => setIsCreateModalOpen(true)}
        className="text-white bg-green-700 hover:bg-green-800 focus:outline-none focus:ring-4 focus:ring-green-300 font-medium rounded-full text-sm px-5 py-2.5 text-center me-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800"
      >
        Create User
      </button>


        <EditUserModal
          user={selectedUser}
          isOpen={isModalOpen}
          onClose={handleCloseModal} // This was wrong: onClose={() => setModalOpen(false)}
          onSave={handleSaveUser}
          roles={roles}
        />
        
        {error && <div className="bg-red-100 p-3 mb-4 text-red-700 rounded">{error}</div>}
        <UserTable
          users={users}
          currentUsers={currentUsers}
          roles={roles}
          loading={loading}
          error={error}
          currentPage={currentPage}
          totalPages={totalPages}
          setCurrentPage={setCurrentPage}
          indexOfFirstUser={indexOfFirstUser}
          csrfToken={csrfToken}
          onEdit={handleEditClick}
           onDelete={handleDelete}
  setUserToDelete={setUserToDelete}
  setIsDeleteModalOpen={setIsDeleteModalOpen}
        />


        <CreateUserModal
  isOpen={isCreateModalOpen}
  onClose={() => setIsCreateModalOpen(false)}
  onSave={handleCreateUser}
  roles={roles}
/>

<DeleteUserModal
  isOpen={isDeleteModalOpen}
  onClose={() => setIsDeleteModalOpen(false)}
  onDelete={handleConfirmDelete}
  userEmail={userToDelete?.email || ''}
  loading={deleting}
/>
<DeleteUserModal
  isOpen={isDeleteModalOpen}
  onClose={() => setIsDeleteModalOpen(false)}
  onDelete={handleConfirmDelete}             // receives email from modal
  userEmail={userToDelete?.email || ''}      // pulls email from selected user
  loading={deleting}
/>

      </div>


    </div>
  );
};

export default UserManagement;