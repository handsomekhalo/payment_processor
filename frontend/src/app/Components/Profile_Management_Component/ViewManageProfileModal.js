"use client";
import React from "react";

export default function ManageProfileModal({ user, profile, merchantProfile, onClose, onEdit }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/50 backdrop-blur-sm">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">My Profile</h3>

        {/* Core User Info */}
        <p><span className="font-semibold">Name:</span> 
        {user.first_name} {user.last_name}
        </p>
        <p><span className="font-semibold">Email:</span> {user.email}</p>
        <p><span className="font-semibold">Role:</span> {user.user_type?.name}</p>
        <p><span className="font-semibold">Phone:</span> {profile.phone_number}</p>
        <p><span className="font-semibold">City:</span> {profile.city}, {profile.province?.name}</p>

        {/* Merchant Info if merchant */}
        {merchantProfile && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Merchant Details</h4>
            <p><span className="font-semibold">Business:</span> {merchantProfile.business_name}</p>
            <p><span className="font-semibold">Reg No:</span> {merchantProfile.registration_number || "N/A"}</p>
            <p><span className="font-semibold">VAT:</span> {merchantProfile.vat_number || "N/A"}</p>
            <p><span className="font-semibold">Compliance:</span> {merchantProfile.compliance_status}</p>
          </div>
        )}

        <div className="flex justify-end space-x-2 mt-6">
          <button
            onClick={onEdit}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500"
          >
            Edit Profile
          </button>
          <button
            onClick={onClose}
            className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
