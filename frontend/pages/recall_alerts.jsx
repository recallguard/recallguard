import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import axios from "axios";
import { motion } from "framer-motion";

export default function RecallAlerts() {
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get("/api/alerts", {
          headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
        });
        setAlerts(data);
      } catch (err) {
        setError("Failed to load alerts");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const markAsRead = async (id) => {
    try {
      await axios.patch(`/api/alerts/${id}`, { read: true }, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
      });
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-bold">Recall Alerts</h1>

        {loading && (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full rounded-xl" />
            ))}
          </div>
        )}

        {error && (
          <p className="text-red-500 text-center py-8">{error}</p>
        )}

        {!loading && alerts?.length === 0 && (
          <p className="text-center text-slate-600 py-8">No active recalls 🎉</p>
        )}

        <div className="space-y-4">
          {alerts?.map((alert, idx) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <Card className="shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="p-6 space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="font-semibold text-lg">{alert.product_name}</h2>
                      <p className="text-sm text-slate-600">
                        Hazard: {alert.hazard || "Unknown"}
                      </p>
                      <p className="text-xs text-slate-500">
                        Recall Date: {new Date(alert.recall_date).toLocaleDateString()}
                      </p>
                    </div>
                    <Button size="sm" onClick={() => markAsRead(alert.id)}>
                      Mark as Read
                    </Button>
                  </div>
                  <a
                    href={alert.recall_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline text-sm"
                  >
                    View official recall notice →
                  </a>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
