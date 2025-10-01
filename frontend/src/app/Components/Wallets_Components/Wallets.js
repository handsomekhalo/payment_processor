"use client";

import React, { useState} from "react";
import { PlusCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import AddWalletModal from "./AddWallets";

export default function Wallets() {
  const [wallets, setWallets] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [coin, setCoin] = useState("");
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");

  const handleAddWallet = () => {
    if (!coin || !address) return;
    setWallets([...wallets, { coin, name, address }]);
    setShowModal(false);
    setCoin("");
    setName("");
    setAddress("");
  };

  return (
    <Card className="w-full p-6 rounded-2xl shadow-sm border">
      <CardContent>
        {wallets.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center py-10">
            <p className="text-gray-500 mb-2">You haven't added any wallets</p>
            <p className="text-sm text-gray-400 mb-4">
              Easily manage your wallet addresses
            </p>
            <Button onClick={() => setShowModal(true)}>
              <PlusCircle className="w-4 h-4 mr-2" />
              Add Wallet(s)
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {wallets.map((wallet, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
              >
                <div>
                  <p className="font-medium">{wallet.name || "Unnamed Wallet"}</p>
                  <p className="text-sm text-gray-500">
                    {wallet.coin} - {wallet.address}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setWallets(wallets.filter((_, i) => i !== index))
                  }
                >
                  Remove
                </Button>
              </div>
            ))}
            <Button onClick={() => setShowModal(true)} className="mt-4">
              <PlusCircle className="w-4 h-4 mr-2" />
              Add Another Wallet
            </Button>
          </div>
        )}
      </CardContent>

      {showModal && (
        <AddWalletModal
          coin={coin}
          setCoin={setCoin}
          name={name}
          setName={setName}
          address={address}
          setAddress={setAddress}
          onSubmit={handleAddWallet}
          onClose={() => setShowModal(false)}
        />
      )}
    </Card>
  );
}
