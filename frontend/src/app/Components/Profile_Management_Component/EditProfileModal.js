"use client";
import React from "react";

export default function EditProfileModal({
  user,
  profile,
  merchantProfile,
  setProfile,
  setMerchantProfile,
  onSubmit,
  onClose,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/70 backdrop-blur-sm">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Edit Profile</h3>

        {/* First + Last Name */}
        <input
          type="text"
          placeholder="First Name"
        //   value={user.first_name}
          onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded mb-3"
        />
        <input
          type="text"
          placeholder="Last Name"
        //   value={user.last_name}
          onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded mb-3"
        />

        {/* Contact */}
        <input
          type="text"
          placeholder="Phone Number"
        //   value={profile.phone_number}
          onChange={(e) => setProfile({ ...profile, phone_number: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded mb-3"
        />
        <input
          type="text"
          placeholder="City"
        //   value={profile.city}
          onChange={(e) => setProfile({ ...profile, city: e.target.value })}
          className="w-full p-2 border border-gray-300 rounded mb-3"
        />

        {/* Merchant Fields if merchant */}
        {merchantProfile && (
          <>
            <input
              type="text"
              placeholder="Business Name"
              value={merchantProfile.business_name}
              onChange={(e) => setMerchantProfile({ ...merchantProfile, business_name: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded mb-3"
            />
            <input
              type="text"
              placeholder="VAT Number"
              value={merchantProfile.vat_number || ""}
              onChange={(e) => setMerchantProfile({ ...merchantProfile, vat_number: e.target.value })}
              className="w-full p-2 border border-gray-300 rounded mb-3"
            />
          </>
        )}

        <div className="flex justify-end space-x-2 mt-6">
          <button
            onClick={onSubmit}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-500"
          >
            Save
          </button>
          <button
            onClick={onClose}
            className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
