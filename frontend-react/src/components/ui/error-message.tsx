import React from "react";
import { Button } from "@/components/ui/button";
import { RotateCw, AlertCircle } from "lucide-react";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onReload?: () => void;
  retryDisabled?: boolean;
}

export default function ErrorMessage({
  message,
  onRetry,
  onReload = () => window.location.reload(),
  retryDisabled = false,
}: ErrorMessageProps) {
  return (
    <div className="border rounded-md p-6 bg-red-50 text-red-600 flex justify-center">
      <div className="flex flex-col items-center max-w-xl">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-5 w-5" />
          <h3 className="font-semibold">Verbindungsfehler</h3>
        </div>
        <p className="mb-4 font-medium text-center">{message}</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {onRetry && (
            <Button
              variant="outline"
              onClick={onRetry}
              className="flex items-center gap-2"
              disabled={retryDisabled}
            >
              <RotateCw className="h-4 w-4" />
              Erneut versuchen
            </Button>
          )}
          <Button
            variant="outline"
            onClick={onReload}
            className="flex items-center gap-2"
          >
            <RotateCw className="h-4 w-4" />
            Seite neu laden
          </Button>
        </div>
      </div>
    </div>
  );
} 