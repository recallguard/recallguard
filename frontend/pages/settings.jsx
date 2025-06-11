import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import axios from "axios";

export default function Settings() {
  // ----------------------- state ------------------------
  const [prefs, setPrefs] = useState({
    emailAlerts: true,
    smsAlerts: false,
    frequency: "immediate", // or "daily"
    phone: "",
  });
  const [original, setOriginal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // ----------------------- effects ----------------------
  useEffect(() => {
    let mounted = true;
    axios
      .get("/preferences")
      .then((res) => {
        if (mounted) {
          setPrefs(res.data);
          setOriginal(res.data);
        }
      })
      .catch(() => {
        /* handle error, maybe toast */
      })
      .finally(() => mounted && setLoading(false));
    return () => (mounted = false);
  }, []);

  // ----------------------- handlers ---------------------
  const handleToggle = (key) => setPrefs((p) => ({ ...p, [key]: !p[key] }));

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put("/preferences", prefs);
      setOriginal(prefs);
      // toast.success("Preferences saved");
    } catch {
      // toast.error("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => original && setPrefs(original);

  const isDirty = JSON.stringify(prefs) !== JSON.stringify(original);

  // ----------------------- render -----------------------
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="animate-pulse text-slate-500">Loading…</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <motion.div
        className="flex-1 flex items-start justify-center p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="w-full max-w-xl shadow-xl rounded-2xl">
          <CardContent className="p-8 space-y-6">
            <h1 className="text-2xl font-semibold">Notification Settings</h1>

            {/* Email alerts */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-medium">Email alerts</h2>
                <p className="text-sm text-slate-600">
                  Receive recall notifications at <strong>{prefs.email}</strong>.
                </p>
              </div>
              <Switch
                checked={prefs.emailAlerts}
                onCheckedChange={() => handleToggle("emailAlerts")}
              />
            </div>

            {/* SMS alerts */}
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h2 className="font-medium">SMS alerts</h2>
                <p className="text-sm text-slate-600">
                  Instant texts for critical recalls.
                </p>
              </div>
              <Switch
                checked={prefs.smsAlerts}
                onCheckedChange={() => handleToggle("smsAlerts")}
              />
            </div>
            {prefs.smsAlerts && (
              <Input
                className="w-full"
                placeholder="Mobile number"
                value={prefs.phone}
                onChange={(e) =>
                  setPrefs((p) => ({ ...p, phone: e.target.value }))
                }
              />
            )}

            {/* Frequency */}
            <div>
              <h2 className="font-medium mb-2">Alert frequency</h2>
              <div className="flex gap-4">
                {["immediate", "daily"].map((opt) => (
                  <Button
                    key={opt}
                    variant={
                      prefs.frequency === opt ? "default" : "outline"
                    }
                    onClick={() =>
                      setPrefs((p) => ({ ...p, frequency: opt }))
                    }
                  >
                    {opt === "immediate" ? "Immediate" : "Daily digest"}
                  </Button>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={handleReset} disabled={!isDirty}>
                Reset
              </Button>
              <Button onClick={handleSave} disabled={!isDirty || saving}>
                {saving ? "Saving…" : "Save"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
