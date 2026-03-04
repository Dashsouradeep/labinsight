"use client";

import { useAuth } from "@/lib/use-auth";
import { useReports } from "@/lib/use-api";
import Header from "@/components/Header";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import Link from "next/link";
import { useRouter } from "next/navigation";

/**
 * Dashboard Page
 * Protected route that displays user's lab reports with processing status
 * 
 * Features:
 * - List of uploaded reports with dates and status
 * - Processing status indicators (uploaded, processing, completed, failed)
 * - Upload new report button
 * - Quick stats: total reports count
 * - Navigation to trends page
 * - Clickable report items to view details
 */
export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const { reports, isLoading: reportsLoading, isError, error, revalidate } = useReports();
  const router = useRouter();

  // Debug logging
  console.log("Dashboard - user:", user);
  console.log("Dashboard - reports data:", reports);
  console.log("Dashboard - isError:", isError);
  console.log("Dashboard - error:", error);
  console.log("Dashboard - isLoading:", reportsLoading);

  if (authLoading || reportsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary-lighter">
        <LoadingSpinner />
      </div>
    );
  }

  // Calculate quick stats - ensure reports is always an array
  const reportsArray = Array.isArray(reports) ? reports : [];
  const totalReports = reportsArray.length;
  const completedReports = reportsArray.filter(r => r.processing_status === "completed").length;
  const processingReports = reportsArray.filter(r => r.processing_status === "processing").length;
  const failedReports = reportsArray.filter(r => r.processing_status === "failed").length;

  // Get status badge styling
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800 border-green-200";
      case "processing":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "uploaded":
        return "bg-gray-100 text-gray-800 border-gray-200";
      case "failed":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="min-h-screen bg-primary-lighter">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-dark mb-2">
            Welcome back, {user?.email?.split("@")[0]}!
          </h1>
          <p className="text-gray-600">
            View your lab reports and track your health trends over time.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Total Reports</div>
            <div className="text-3xl font-bold text-primary-dark">{totalReports}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Completed</div>
            <div className="text-3xl font-bold text-green-600">{completedReports}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Processing</div>
            <div className="text-3xl font-bold text-blue-600">{processingReports}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Failed</div>
            <div className="text-3xl font-bold text-red-600">{failedReports}</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <Link
            href="/upload"
            className="inline-flex items-center justify-center px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium shadow-md"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Upload New Report
          </Link>
          {completedReports >= 2 && (
            <Link
              href="/trends"
              className="inline-flex items-center justify-center px-6 py-3 bg-primary-medium text-white rounded-lg hover:bg-primary transition-colors font-medium shadow-md"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                />
              </svg>
              View Health Trends
            </Link>
          )}
        </div>

        {/* Error Display */}
        {isError && (
          <div className="mb-8">
            <ErrorMessage
              message="Failed to load reports. Please try again."
              onRetry={revalidate}
            />
          </div>
        )}

        {/* Reports List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-primary-dark">
              Your Lab Reports
            </h2>
          </div>

          {!reportsArray || reportsArray.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400 mb-4"
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
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No reports yet
              </h3>
              <p className="text-gray-600 mb-6">
                Upload your first lab report to get started with AI-powered health insights.
              </p>
              <Link
                href="/upload"
                className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
              >
                Upload Your First Report
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {reportsArray.map((report) => (
                <div
                  key={report.id}
                  onClick={() => {
                    if (report.processing_status === "completed") {
                      router.push(`/reports/${report.id}`);
                    }
                  }}
                  className={`px-6 py-4 hover:bg-gray-50 transition-colors ${
                    report.processing_status === "completed"
                      ? "cursor-pointer"
                      : "cursor-default"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {report.file_name}
                        </h3>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusBadge(
                            report.processing_status
                          )}`}
                        >
                          {report.processing_status.charAt(0).toUpperCase() +
                            report.processing_status.slice(1)}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center">
                          <svg
                            className="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                          </svg>
                          {formatDate(report.upload_date)}
                        </span>
                        <span className="flex items-center">
                          <svg
                            className="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                            />
                          </svg>
                          {formatFileSize(report.file_size)}
                        </span>
                        <span className="flex items-center">
                          <svg
                            className="w-4 h-4 mr-1"
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
                          {report.file_type}
                        </span>
                      </div>
                      {report.error_message && (
                        <div className="mt-2 text-sm text-red-600">
                          Error: {report.error_message}
                        </div>
                      )}
                    </div>
                    {report.processing_status === "completed" && (
                      <div className="ml-4">
                        <svg
                          className="w-5 h-5 text-gray-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Helpful Tips */}
        {totalReports > 0 && completedReports < 2 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
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
                <h3 className="text-sm font-medium text-blue-900 mb-1">
                  Track Your Health Over Time
                </h3>
                <p className="text-sm text-blue-700">
                  Upload at least 2 reports to unlock health trend analysis and see how your parameters change over time.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
