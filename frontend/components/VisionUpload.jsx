import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

/**
 * VisionUpload – drag‑and‑drop uploader that snaps a product photo,
 * sends it to /products/vision, and surfaces success/error state.
 *
 * Props:
 *   onSuccess?: (product) => void  // callback with ProductOut JSON
 */
export default function VisionUpload({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [message, setMessage] = useState("");

  const onDrop = useCallback(async (accepted) => {
    if (!accepted?.length) return;
    const img = accepted[0];
    setFile(Object.assign(img, { preview: URL.createObjectURL(img) }));
    setStatus("uploading");

    const form = new FormData();
    form.append("file", img);

    try {
      const { data } = await axios.post("/products/vision", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus("success");
      setMessage(`${data.name} added to watch‑list`);
      onSuccess?.(data);
    } catch (err) {
      setStatus("error");
      setMessage(
        err.response?.data?.detail || "Could not extract a valid barcode."
      );
    }
  }, [onSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "image/*": [] },
    maxFiles: 1,
    onDrop,
  });

  const reset = () => {
    if (file?.preview) URL.revokeObjectURL(file.preview);
    setFile(null);
    setStatus("idle");
    setMessage("");
  };

  return (
    <Card className="shadow-lg rounded-2xl">
      <CardContent className="p-6 flex flex-col gap-4 items-center">
        {status === "idle" && (
          <div
            {...getRootProps({
              className:
                "w-full h-48 border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center cursor-pointer bg-slate-50 hover:border-primary transition",
            })}
          >
            <input {...getInputProps()} />
            <p className="text-slate-600 text-sm">
              {isDragActive ? "Drop the image here …" : "Drag & drop a photo or click to upload"}
            </p>
          </div>
        )}

        {file && (
          <motion.img
            src={file.preview}
            alt="Preview"
            className="w-40 h-40 object-cover rounded-lg shadow"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          />
        )}

        {/* Status feedback */}
        {status === "uploading" && (
          <div className="flex items-center gap-2 text-primary">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Scanning…</span>
          </div>
        )}
        {status === "success" && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="w-5 h-5" />
            <span className="text-sm">{message}</span>
          </div>
        )}
        {status === "error" && (
          <div className="flex items-center gap-2 text-red-600">
            <XCircle className="w-5 h-5" />
            <span className="text-sm">{message}</span>
          </div>
        )}

        {(status === "success" || status === "error") && (
          <Button variant="outline" size="sm" onClick={reset}>
            Upload another
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
