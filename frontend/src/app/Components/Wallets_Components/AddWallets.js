"use client";
import React from "react";

export default function AddWalletModal({
  coin,
  setCoin,
  name,
  setName,
  address,
  setAddress,
  onSubmit,
  onClose,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/50 backdrop-blur-sm">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Add a Wallet</h3>

        {/* Select Coin */}
        <select
          value={coin}
          onChange={(e) => setCoin(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-4"
        >
          <option value="">Select Coin</option>
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
          <option value="USDT">Tether (USDT)</option>
        </select>

        {/* Wallet Name */}
        <input
          type="text"
          placeholder="Wallet Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-4"
        />

        {/* Wallet Address */}
        <input
          type="text"
          placeholder="Wallet Address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-4"
        />

        {/* Action Buttons */}
        <div className="flex justify-end space-x-2">
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
