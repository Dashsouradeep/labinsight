"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { useAuth } from "@/lib/use-auth";
import { uploadFile, getErrorMessage } from "@/lib/api-client";
import Header from "@/components/Header";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";

/**
 * Upload Page
 * Allows users to upload lab reports with drag-and-drop functionality
 * 
 * Features:
 * - Drag-and-drop file upload zone using react-dropzone
 * - File type validation (PDF, JPEG, PNG only)
 * - File size validation (max 10MB)
 * - Upload progress indicator
 * - Processing status display after upload
 * - Success/error messages
 * - Navigation back to dashboard after successful upload
 * 
 * Requirements: 11.5
 */

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
const ACCEPTED_FILE_TYPES = {
  "application/pdf": [".pdf"],
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
};

type UploadStatus = "idle" | "uploading" | "processing" | "success" | "error";

export default function UploadPage() {
  const { user, session, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const token = session?.user?.accessToken;
  
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [reportId, setReportId] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Clear previous errors
    setErrorMessage("");
    setUploadStatus("idle");
    
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === "file-too-large") {
        setErrorMessage("File size exceeds 10MB limit. Please upload a smaller file.");
      } else if (rejection.errors[0]?.code === "file-invalid-type") {
        setErrorMessage("Invalid file type. Please upload a PDF, JPEG, or PNG file.");
      } else {
        setErrorMessage("File validation failed. Please try again.");
      }
      setUploadStatus("error");
      return;
    }

    // Handle accepted files
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  });

  // Handle file upload
  const handleUpload = async () => {
    if (!selectedFile || !token) {
      setErrorMessage("Please select a file to upload.");
      setUploadStatus("error");
      return;
    }

    try {
      setUploadStatus("uploading");
      setUploadProgress(0);
      setErrorMessage("");

      // Simulate upload progress (since we don't have real progress tracking)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Upload the file
      const response = await uploadFile("/api/reports/upload", selectedFile, token, {
        revalidate: "/api/reports",
        timeout: 60000, // 60 second timeout
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      // Store report ID and update status
      setReportId(response.report_id);
      setUploadStatus("processing");

      // Redirect to dashboard after 3 seconds
      setTimeout(() => {
        router.push("/dashboard");
      }, 3000);
    } catch (error) {
      setUploadStatus("error");
      setErrorMessage(getErrorMessage(error));
      setUploadProgress(0);
    }
  };

  // Handle retry
  const handleRetry = () => {
    setUploadStatus("idle");
    setErrorMessage("");
    setUploadProgress(0);
    setSelectedFile(null);
  };

  // Handle cancel
  const handleCancel = () => {
    setSelectedFile(null);
    setUploadStatus("idle");
    setErrorMessage("");
    setUploadProgress(0);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary-lighter">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary-lighter">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-dark mb-2">
            Upload Lab Report
          </h1>
          <p className="text-gray-600">
            Upload your lab report in PDF, JPEG, or PNG format (max 10MB)
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {/* Drag and Drop Zone */}
          {uploadStatus === "idle" && !selectedFile && (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                isDragActive && !isDragReject
                  ? "border-primary bg-primary-lighter"
                  : isDragReject
                  ? "border-red-500 bg-red-50"
                  : "border-gray-300 hover:border-primary hover:bg-gray-50"
              }`}
            >
              <input {...getInputProps()} />
              <div className="flex flex-col items-center">
                <svg
                  className={`w-16 h-16 mb-4 ${
                    isDragActive && !isDragReject
                      ? "text-primary"
                      : isDragReject
                      ? "text-red-500"
                      : "text-gray-400"
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                {isDragActive && !isDragReject ? (
                  <p className="text-lg font-medium text-primary mb-2">
                    Drop your file here
                  </p>
                ) : isDragReject ? (
                  <p className="text-lg font-medium text-red-600 mb-2">
                    Invalid file type or size
                  </p>
                ) : (
                  <>
                    <p className="text-lg font-medium text-gray-900 mb-2">
                      Drag and drop your lab report here
                    </p>
                    <p className="text-sm text-gray-600 mb-4">or</p>
                    <button
                      type="button"
                      className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium"
                    >
                      Browse Files
                    </button>
                  </>
                )}
                <p className="text-xs text-gray-500 mt-4">
                  Supported formats: PDF, JPEG, PNG (max 10MB)
                </p>
              </div>
            </div>
          )}

          {/* Selected File Display */}
          {selectedFile && uploadStatus === "idle" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <svg
                    className="w-10 h-10 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-600">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleCancel}
                  className="text-gray-500 hover:text-red-600 transition-colors"
                  aria-label="Remove file"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleUpload}
                  className="flex-1 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium"
                >
                  Upload Report
                </button>
                <button
                  onClick={handleCancel}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Uploading State */}
          {uploadStatus === "uploading" && (
            <div className="space-y-4">
              <div className="flex items-center justify-center mb-4">
                <LoadingSpinner size="lg" label="Uploading file..." />
              </div>
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Uploading {selectedFile?.name}</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-primary h-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Processing State */}
          {uploadStatus === "processing" && (
            <div className="text-center py-8">
              <div className="flex justify-center mb-4">
                <svg
                  className="w-16 h-16 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Upload Successful!
              </h3>
              <p className="text-gray-600 mb-4">
                Your report is being processed. This may take a few moments.
              </p>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <LoadingSpinner size="sm" label="Processing..." />
                <span>Processing your report...</span>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                Redirecting to dashboard...
              </p>
            </div>
          )}

          {/* Error State */}
          {uploadStatus === "error" && errorMessage && (
            <div className="space-y-4">
              <ErrorMessage message={errorMessage} onRetry={handleRetry} />
              <button
                onClick={handleRetry}
                className="w-full px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Try Again
              </button>
            </div>
          )}
        </div>

        {/* Information Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start">
            <svg
              className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-2">
                What happens after upload?
              </h3>
              <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                <li>Your report will be processed using AI technology</li>
                <li>Medical parameters will be extracted and analyzed</li>
                <li>You'll receive easy-to-understand explanations</li>
                <li>Processing typically takes 20-30 seconds</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
