import React from "react";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

/**
 * AlertModal – reusable modal that shows detailed recall information.
 *
 * Props:
 *   open         – boolean, controlled
 *   onOpenChange – fn(boolean)
 *   product      – { name, identifier }
 *   recall       – { hazard, remedy, link, recall_date }
 */
export default function AlertModal({ open, onOpenChange, product, recall }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        {/* parent controls the trigger (e.g., Details button) */}
      </DialogTrigger>
      <DialogContent className="max-w-lg sm:max-w-xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <DialogHeader>
            <DialogTitle>Recall Details</DialogTitle>
            <DialogDescription>
              <span className="font-semibold">{product.name}</span> — ID {product.identifier}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            <div>
              <h3 className="font-medium text-slate-700 mb-1">Hazard</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                {recall.hazard || "No hazard description provided."}
              </p>
            </div>
            {recall.remedy && (
              <div>
                <h3 className="font-medium text-slate-700 mb-1">Recommended Remedy</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  {recall.remedy}
                </p>
              </div>
            )}
            <div>
              <h3 className="font-medium text-slate-700 mb-1">Recall Date</h3>
              <p className="text-slate-600 text-sm">
                {new Date(recall.recall_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <DialogFooter className="mt-6">
            <Button asChild>
              <a href={recall.link} target="_blank" rel="noopener noreferrer">
                View Official Notice
              </a>
            </Button>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </DialogFooter>
        </motion.div>
      </DialogContent>
    </Dialog>
  );
}
