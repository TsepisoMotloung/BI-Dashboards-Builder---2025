"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function ErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error") || "unknown";
  const callbackUrl = searchParams.get("callbackUrl");

  const [errorDetails, setErrorDetails] = useState<string>("");
  const [allParams, setAllParams] = useState<Record<string, string>>({});

  useEffect(() => {
    // Collect all URL parameters for debugging
    const params: Record<string, string> = {};
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
    setAllParams(params);

    // Log error to console
    console.error("Auth Error Page - Parameters:", params);
    console.error("Auth Error Code:", error);

    // Provide error details
    const errorMessages: Record<string, string> = {
      callback: "Callback error - Failed to complete authentication callback",
      credentials: "Invalid email or password",
      default: "An authentication error occurred",
      unknown: "Unknown authentication error",
    };

    setErrorDetails(errorMessages[error] || errorMessages.unknown);
  }, [error, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-red-600">
            Authentication Error
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            There was a problem signing you in
          </p>
        </div>

        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{errorDetails}</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  <strong>Error Code:</strong> {error}
                </p>
                {callbackUrl && (
                  <p className="mt-1">
                    <strong>Callback URL:</strong> {callbackUrl}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Debug Info */}
        <details className="text-xs">
          <summary className="cursor-pointer text-gray-600 hover:text-gray-900">
            Debug Information
          </summary>
          <pre className="mt-2 p-2 bg-gray-100 rounded text-gray-800 overflow-auto max-h-48">
            {JSON.stringify(allParams, null, 2)}
          </pre>
        </details>

        <div className="flex gap-4">
          <Link
            href="/auth/signin"
            className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-center"
          >
            Try Again
          </Link>
          <Link
            href="/"
            className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 text-center"
          >
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}
