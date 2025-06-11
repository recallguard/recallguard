import React, { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import axios from "axios";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function B2BDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    axios
      .get("/admin/b2b/metrics")
      .then((res) => mounted && setStats(res.data))
      .catch((e) => console.error(e))
      .finally(() => mounted && setLoading(false));
    return () => (mounted = false);
  }, []);

  if (loading || !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Skeleton className="w-72 h-16" />
      </div>
    );
  }

  const barData = {
    labels: stats.last12Months.labels,
    datasets: [
      {
        label: "New Partners",
        data: stats.last12Months.partners,
        backgroundColor: "rgba(59,130,246,0.6)",
        borderRadius: 8,
      },
    ],
  };

  const lineData = {
    labels: stats.last12Months.labels,
    datasets: [
      {
        label: "Replacement Orders",
        data: stats.last12Months.replacements,
        fill: false,
        borderColor: "rgba(16,185,129,0.8)",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <motion.div
        className="p-6 max-w-6xl mx-auto w-full flex flex-col gap-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold">B2B Partner Dashboard</h1>

        {/* KPI cards */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Total Partners", value: stats.totalPartners },
            { label: "Active Campaigns", value: stats.activeCampaigns },
            { label: "Monthly Revenue", value: `$${stats.mrr}` },
            { label: "Avg. Conversion", value: `${stats.avgConversion}%` },
          ].map(({ label, value }, i) => (
            <Card key={i} className="shadow-lg rounded-2xl">
              <CardContent className="p-6">
                <p className="text-sm text-slate-500 mb-1">{label}</p>
                <p className="text-2xl font-semibold text-slate-800">{value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts */}
        <div className="grid gap-8 lg:grid-cols-2">
          <Card className="shadow-lg rounded-2xl">
            <CardContent className="p-6">
              <h2 className="font-medium mb-4">New Partners (last 12 months)</h2>
              <Bar data={barData} options={{ plugins: { legend: { display: false } } }} />
            </CardContent>
          </Card>

          <Card className="shadow-lg rounded-2xl">
            <CardContent className="p-6">
              <h2 className="font-medium mb-4">Replacement Orders (last 12 months)</h2>
              <Line data={lineData} options={{ plugins: { legend: { display: false } } }} />
            </CardContent>
          </Card>
        </div>

        {/* Partner table */}
        <Card className="shadow-lg rounded-2xl">
          <CardContent className="p-6 overflow-x-auto">
            <h2 className="font-medium mb-4">Recent Partner Sign‑ups</h2>
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-slate-600 border-b">
                  <th className="py-2 pr-4">Company</th>
                  <th className="py-2 pr-4">Industry</th>
                  <th className="py-2 pr-4">Joined</th>
                  <th className="py-2 pr-4">Plan</th>
                  <th className="py-2 pr-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recentPartners.map((p, idx) => (
                  <tr key={idx} className="border-b last:border-none">
                    <td className="py-2 pr-4 whitespace-nowrap font-medium">{p.company}</td>
                    <td className="py-2 pr-4">{p.industry}</td>
                    <td className="py-2 pr-4">{p.joined}</td>
                    <td className="py-2 pr-4">{p.plan}</td>
                    <td className="py-2 pr-0 text-right">
                      <Button size="sm" variant="outline">
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
