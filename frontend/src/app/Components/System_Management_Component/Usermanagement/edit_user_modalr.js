import React, { useState, useEffect } from 'react';

const EditUserModal = ({ user, isOpen, onClose, onSave, roles }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role: '',
  });
  
  useEffect(() => {
    if (user) {
      // Determine the correct role value
      // It might be in user.user_type_id or user.user_type.id
      let roleValue = '';
      
      if (user.user_type_id !== undefined && user.user_type_id !== null) {
        roleValue = user.user_type_id.toString();
      } else if (user.user_type && user.user_type.id !== undefined) {
        roleValue = user.user_type.id.toString();
      }
      
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        role: roleValue,
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = () => {
    // Validate form before submitting
    if (!formData.first_name || !formData.last_name || !formData.email) {
      alert('Please fill in all required fields');
      return;
    }
    
    onSave(user.id, formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded shadow-md w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Edit User</h2>
        <div className="mb-4">
          <label className="block font-medium">First Name *</label>
          <input
            type="text"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded mt-1"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block font-medium">Last Name *</label>
          <input
            type="text"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded mt-1"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block font-medium">Email *</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded mt-1"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block font-medium">Role *</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded mt-1"
            required
          >
            <option value="">Select Role</option>
            {Array.isArray(roles) && roles.map((role) => (
              <option key={role.id} value={role.id.toString()}>
                {role.name}
              </option>
            ))}
          </select>
          {!formData.role && (
            <p className="text-red-500 text-sm mt-1">Please select a role</p>
          )}
        </div>
        <div className="flex justify-end space-x-2">
          <button onClick={onClose} className="bg-gray-300 px-4 py-2 rounded">
            Cancel
          </button>
          <button 
            onClick={handleSubmit} 
            className={`bg-blue-500 text-white px-4 py-2 rounded ${!formData.role ? 'opacity-50' : ''}`}
            disabled={!formData.role}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditUserModal;