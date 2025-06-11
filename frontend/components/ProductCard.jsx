import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";

/**
 * ProductCard
 * -----------
 * Displays a tracked product’s image, name, identifier, and recall status.
 *
 * Props
 * -----
 * product: {
 *   id: number;
 *   name: string;
 *   identifier: string; // UPC, VIN, etc.
 *   imageUrl?: string;
 *   recalled: boolean;
 *   recallId?: string;   // present if recalled
 *   recallDate?: string; // ISO date string
 * }
 * onViewDetails: (id: number) => void;
 */
export default function ProductCard({ product, onViewDetails }) {
  const {
    id,
    name,
    identifier,
    imageUrl = "/placeholder.png",
    recalled,
    recallDate,
  } = product;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="shadow-md rounded-xl">
        <CardContent className="p-4 flex gap-4">
          {/* Product image */}
          <img
            src={imageUrl}
            alt={name}
            className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
          />

          {/* Details */}
          <div className="flex-1">
            <h3 className="font-semibold text-sm md:text-base">{name}</h3>
            <p className="text-xs text-slate-500 break-all">{identifier}</p>

            {recalled ? (
              <div className="mt-2 flex items-center gap-1 text-red-600 text-xs">
                <ShieldAlert className="w-4 h-4" />
                <span>Recalled {new Date(recallDate).toLocaleDateString()}</span>
              </div>
            ) : (
              <p className="mt-2 text-xs text-green-600">No recalls</p>
            )}
          </div>

          {/* Actions */}
          {recalled && (
            <Button size="sm" onClick={() => onViewDetails(id)}>
              Details
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
