import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

/**
 * Simple user dashboard – shows aggregate metrics plus a recall‑timeline chart.
 * Data is fetched from /api/dashboard (JSON) which returns:
 *   {
 *     products: number,
 *     recalls: number,
 *     pendingAlerts: number,
 *     chart: { labels: string[], counts: number[] }
 *   }
 */

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/dashboard")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="flex-1 p-8 grid gap-6 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-slate-500">Failed to load dashboard data.</p>
        </div>
      </div>
    );
  }

  const stats = [
    { label: "Tracked Products", value: data.products, emoji: "📦" },
    { label: "Total Recalls", value: data.recalls, emoji: "🚨" },
    { label: "Pending Alerts", value: data.pendingAlerts, emoji: "⚠️" },
  ];

  const chartData = {
    labels: data.chart.labels,
    datasets: [
      {
        label: "Recalls per Month",
        data: data.chart.counts,
        backgroundColor: "rgba(59, 130, 246, 0.6)",
        borderRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: false },
    },
    scales: {
      y: { grid: { display: false }, beginAtZero: true },
      x: { grid: { display: false } },
    },
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-white to-slate-50">
      <Navbar />

      {/* Stat cards */}
      <section className="flex-1 p-8 grid gap-6 md:grid-cols-3 max-w-6xl mx-auto w-full">
        {stats.map(({ label, value, emoji }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="shadow-xl rounded-2xl">
              <CardContent className="p-6 flex items-center gap-4">
                <span className="text-4xl">{emoji}</span>
                <div>
                  <p className="text-3xl font-bold">{value}</p>
                  <p className="text-slate-600">{label}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* Chart */}
      <section className="pb-16 px-8 max-w-5xl mx-auto w-full">
        <Card className="shadow-xl rounded-2xl">
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-4">Recall Trend</h2>
            <Bar data={chartData} options={chartOptions} height={320} />
          </CardContent>
        </Card>
      </section>

      <footer className="py-8 text-center text-sm text-slate-500">
        Need help? <Button variant="link" size="sm">Contact Support</Button>
      </footer>
    </div>
  );
}
