'use client'

import { useState } from "react";
import ManageProfileModal
 from "./ViewManageProfileModal";
import EditProfileModal from "./EditProfileModal";

export default function ProfileSection() {
  const [showManage, setShowManage] = useState(false);
  const [showEdit, setShowEdit] = useState(false);

  const [user, setUser] = useState({
    first_name: "John",
    last_name: "Doe",
    email: "john@example.com",
    user_type: { name: "Merchant" },
  });

  const [profile, setProfile] = useState({
    phone_number: "0812345678",
    city: "Johannesburg",
  });

  const [merchantProfile, setMerchantProfile] = useState({
    business_name: "Doe Traders",
    vat_number: "123456789",
    compliance_status: "VERIFIED",
  });

  const handleSaveProfile = () => {
    console.log("Updated Profile:", { user, profile, merchantProfile });
    setShowEdit(false);
  };

  return (
    <div>
      <button
        onClick={() => setShowManage(true)}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Manage Profile
      </button>

      {showManage && (
        <ManageProfileModal
          user={user}
          profile={profile}
          merchantProfile={merchantProfile}
          onClose={() => setShowManage(false)}
          onEdit={() => {
            setShowManage(false);
            setShowEdit(true);
          }}
        />
      )}

      {showEdit && (
        <EditProfileModal
          user={user}
          profile={profile}
          merchantProfile={merchantProfile}
          setProfile={setProfile}
          setMerchantProfile={setMerchantProfile}
          onSubmit={handleSaveProfile}
          onClose={() => setShowEdit(false)}
        />
      )}
    </div>
  );
}
