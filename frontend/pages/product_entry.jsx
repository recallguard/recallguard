import React, { useState } from "react";
import Navbar from "../components/Navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import axios from "axios";

export default function ProductEntry() {
  const [identifier, setIdentifier] = useState("");
  const [type, setType] = useState("UPC");
  const [isLoading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const endpoint = type === "VIN" ? "/products/vin" : "/products/manual";
      const payload = type === "VIN" ? { vin: identifier } : { identifier };
      const { data } = await axios.post(endpoint, payload, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-slate-50 to-slate-100">
      <Navbar />

      <motion.main
        className="flex flex-col flex-1 items-center justify-center p-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="w-full max-w-lg shadow-xl rounded-2xl">
          <CardContent className="p-8 space-y-6">
            <h1 className="text-2xl font-bold text-center">Add a Product</h1>
            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="type">
                  Identifier Type
                </label>
                <select
                  id="type"
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full border rounded-md p-2"
                >
                  <option value="UPC">UPC / EAN</option>
                  <option value="VIN">VIN</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="identifier">
                  {type}
                </label>
                <Input
                  id="identifier"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder={`Enter ${type}`}
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Adding..." : "Add Product"}
              </Button>
            </form>

            {result && (
              <motion.div
                className="p-4 bg-green-50 border border-green-200 rounded-md text-green-800"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                Added: {result.name || result.identifier}
              </motion.div>
            )}

            {error && (
              <motion.div
                className="p-4 bg-red-50 border border-red-200 rounded-md text-red-800"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {error}
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.main>
    </div>
  );
}
