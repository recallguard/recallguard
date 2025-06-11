import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import axios from "axios";
import { saveAs } from "file-saver";

export default function LeadReport() {
  // ───────────────────────────────────────────── state
  const [rows, setRows] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  // ───────────────────────────────────────────── data fetch
  useEffect(() => {
    let mounted = true;
    axios
      .get("/admin/leads")
      .then((res) => mounted && setRows(res.data))
      .catch(() => {
        /* TODO: toast error */
      })
      .finally(() => mounted && setLoading(false));

    return () => (mounted = false);
  }, []);

  // ───────────────────────────────────────────── helpers
  const downloadCsv = async () => {
    setDownloading(true);
    try {
      const { data } = await axios.get("/admin/leads/export", {
        responseType: "blob",
      });
      saveAs(data, `leads-${new Date().toISOString().slice(0, 10)}.csv`);
    } finally {
      setDownloading(false);
    }
  };

  const markContacted = async (id) => {
    // Optimistic UI
    setRows((prev) =>
      prev.map((r) => (r.id === id ? { ...r, contacted: true } : r)),
    );
    try {
      await axios.patch(`/admin/leads/${id}`, { contacted: true });
    } catch {
      // revert on failure
      setRows((prev) =>
        prev.map((r) => (r.id === id ? { ...r, contacted: false } : r)),
      );
    }
  };

  // ───────────────────────────────────────────── render
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <motion.div
        className="flex-1 p-6 max-w-7xl mx-auto w-full"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-semibold">Lead Report</h1>
          <Button onClick={downloadCsv} disabled={downloading}>
            {downloading ? "Downloading…" : "Export CSV"}
          </Button>
        </div>

        <Card>
          <CardContent className="p-0 overflow-x-auto">
            {loading ? (
              <Skeleton className="h-96 w-full" />
            ) : (
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-100 text-slate-600 text-sm">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Name</th>
                    <th className="px-4 py-3 text-left font-medium">Email</th>
                    <th className="px-4 py-3 text-left font-medium">Company</th>
                    <th className="px-4 py-3 text-left font-medium">
                      Plan Interest
                    </th>
                    <th className="px-4 py-3 text-left font-medium">
                      Date Captured
                    </th>
                    <th className="px-4 py-3 text-left font-medium">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {rows.map((lead) => (
                    <tr
                      key={lead.id}
                      className={
                        lead.contacted
                          ? "bg-green-50"
                          : "hover:bg-slate-50 transition"
                      }
                    >
                      <td className="px-4 py-3 whitespace-nowrap">
                        {lead.name}
                      </td>
                      <td className="px-4 py-3">{lead.email}</td>
                      <td className="px-4 py-3">{lead.company}</td>
                      <td className="px-4 py-3">{lead.plan}</td>
                      <td className="px-4 py-3">
                        {new Date(lead.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        {lead.contacted ? (
                          <span className="text-green-600 font-medium">
                            Contacted
                          </span>
                        ) : (
                          <span className="text-slate-500">Pending</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {!lead.contacted && (
                          <Button
                            size="sm"
                            onClick={() => markContacted(lead.id)}
                          >
                            Mark Contacted
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
