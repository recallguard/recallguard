import React from "react";
import Navbar from "../components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-slate-50 to-slate-100">
      <Navbar />

      {/* Hero */}
      <header className="flex flex-1 flex-col items-center justify-center text-center px-6">
        <motion.h1
          className="font-extrabold text-4xl sm:text-5xl md:text-6xl max-w-4xl leading-tight"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          Never Miss a Recall&nbsp;
          <span className="text-primary">Again</span>
        </motion.h1>
        <p className="mt-6 max-w-xl text-lg text-slate-600">
          RecallGuard watches every purchase you’ve ever made—so you don’t
          have to—and alerts you the instant something is recalled.
        </p>

        <motion.div
          className="mt-8 flex gap-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Button size="lg">Get Started Free</Button>
          <Button variant="outline" size="lg">
            How It Works
          </Button>
        </motion.div>
      </header>

      {/* Benefit cards */}
      <section className="py-16 px-6 grid gap-8 md:grid-cols-3 max-w-6xl mx-auto">
        {[
          {
            title: "Automatic Imports",
            desc: "Connect Gmail or Amazon and we’ll add every past purchase in seconds.",
            icon: "📦",
          },
          {
            title: "Real-Time Alerts",
            desc: "We poll CPSC, FDA, USDA & NHTSA every hour. You get notified instantly.",
            icon: "⚡",
          },
          {
            title: "One-Click Replacements",
            desc: "Partner discounts on safe alternatives when your product is recalled.",
            icon: "💸",
          },
        ].map(({ title, desc, icon }, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="shadow-xl rounded-2xl">
              <CardContent className="p-8 text-center space-y-4">
                <div className="text-4xl">{icon}</div>
                <h3 className="font-semibold text-xl">{title}</h3>
                <p className="text-slate-600">{desc}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} RecallGuard — All rights reserved.
      </footer>
    </div>
  );
}
