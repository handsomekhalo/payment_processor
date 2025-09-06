'use client';
import React from 'react';

  const UserTable = ({ users, currentUsers, loading, error, currentPage, totalPages, setCurrentPage, indexOfFirstUser, onEdit, onDelete,
  setUserToDelete, setIsDeleteModalOpen, }) => (
    <div>
      {loading ? (
        <div className="flex justify-center items-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-blue-500" />
        </div>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <>
          <table className="min-w-full bg-white border border-gray-200 shadow-md rounded overflow-hidden">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left">S.N</th>
                <th className="px-4 py-2 text-left">Full Name</th>
                <th className="px-4 py-2 text-left">Email</th>
                <th className="px-4 py-2 text-left">Role</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {currentUsers.map((user, index) => (
                <tr key={user.id} className="border-t">
                  <td className="px-4 py-2">{index + 1 + indexOfFirstUser}</td>
                  <td className="px-4 py-2">{user.first_name} {user.last_name}</td>
                  <td className="px-4 py-2">{user.email}</td>
                  <td className="px-4 py-2">{user.user_type__name || user.user_type?.name || 'Unknown Role'}</td>
                  <td className="px-4 py-2">
                    <button className="text-blue-600 hover:underline mr-2" onClick={() => onEdit(user)}>Edit</button>
                    {/* <button className="text-red-600 hover:underline">Delete</button>
                    <button className="text-red-600 hover:underline" onClick={() => onDelete(user)}>Delete</button> */}
      {/* <button className="text-red-600 hover:underline" onClick={() => onDelete(user.email)}>
  Delete
</button> */}
<button
  className="text-red-600 hover:underline"
  onClick={() => {
    setUserToDelete(user);        // <=== Set the actual user object
    setIsDeleteModalOpen(true);   // <=== Show modal
  }}
>
  Delete
</button>

                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="flex justify-center mt-4">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded mr-2 disabled:opacity-50"
            >
              Previous
            </button>
            {[...Array(totalPages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i + 1)}
                className={`px-3 py-1 border rounded mx-1 ${currentPage === i + 1 ? 'bg-blue-500 text-white' : ''}`}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded ml-2 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );

  export default UserTable;
