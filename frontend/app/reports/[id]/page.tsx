"use client";

import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/use-auth";
import { useReport } from "@/lib/use-api";
import Header from "@/components/Header";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import ParameterCard from "@/components/ParameterCard";
import Link from "next/link";

/**
 * ReportDetailPage
 * Displays detailed analysis of a specific lab report
 * 
 * Features:
 * - Report metadata (file name, upload date)
 * - General medical disclaimer banner
 * - Parameter table with ParameterCard components
 * - AI-generated overall summary
 * - Lifestyle recommendations
 * - Download original report button
 * 
 * Requirements: 11.6
 */
export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params?.id as string;
  
  const { user, isLoading: authLoading } = useAuth();
  const { report, isLoading: reportLoading, isError, error, revalidate } = useReport(reportId);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Check if there are any critical or mild abnormal parameters
  const hasCriticalParameters = report?.parameters?.some(p => p.risk_level === "Critical");
  const hasMildAbnormalParameters = report?.parameters?.some(p => p.risk_level === "Mild Abnormal");

  // Collect all lifestyle recommendations
  const allRecommendations = report?.parameters
    ?.filter(p => p.lifestyle_recommendations && p.lifestyle_recommendations.length > 0)
    .flatMap(p => p.lifestyle_recommendations.map(rec => ({ parameter: p.name, recommendation: rec }))) || [];

  // Remove duplicates
  const uniqueRecommendations = Array.from(
    new Map(allRecommendations.map(item => [item.recommendation, item])).values()
  );

  if (authLoading || reportLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary-lighter">
        <LoadingSpinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-primary-lighter">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ErrorMessage
            message="Failed to load report details. The report may not exist or you don't have permission to view it."
            onRetry={revalidate}
          />
          <div className="mt-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center text-primary hover:text-primary-dark"
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
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back to Dashboard
            </Link>
          </div>
        </main>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary-lighter">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary-lighter">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-6">
          <Link
            href="/dashboard"
            className="inline-flex items-center text-primary hover:text-primary-dark transition-colors"
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
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Dashboard
          </Link>
        </div>

        {/* Report Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="mb-4 md:mb-0">
              <h1 className="text-3xl font-bold text-primary-dark mb-2">
                Lab Report Analysis
              </h1>
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-gray-600">
                <div className="flex items-center">
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
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <span className="font-medium">{report.file_name}</span>
                </div>
                <div className="flex items-center">
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
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <span>{formatDate(report.upload_date)}</span>
                </div>
              </div>
            </div>
            <div>
              <button
                onClick={() => {
                  // Download functionality - will be implemented when backend provides download endpoint
                  window.open(`${process.env.NEXT_PUBLIC_API_URL}/api/reports/${reportId}/download`, '_blank');
                }}
                className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors shadow-md"
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
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Download Original Report
              </button>
            </div>
          </div>
        </div>

        {/* General Disclaimer */}
        <DisclaimerBanner type="general" />

        {/* Critical Alert (if any critical parameters) */}
        {hasCriticalParameters && (
          <DisclaimerBanner type="critical" />
        )}

        {/* Mild Abnormal Alert (if any mild abnormal parameters and no critical) */}
        {hasMildAbnormalParameters && !hasCriticalParameters && (
          <DisclaimerBanner type="mild" />
        )}

        {/* Overall Summary */}
        {report.summary && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-semibold text-primary-dark mb-4">
              Overall Summary
            </h2>
            <p className="text-base text-gray-700 leading-relaxed">
              {report.summary}
            </p>
            {report.overall_assessment && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-base text-gray-700 leading-relaxed">
                  {report.overall_assessment}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Parameters Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-primary-dark mb-4">
            Lab Parameters
          </h2>
          {report.parameters && report.parameters.length > 0 ? (
            <div className="space-y-4">
              {report.parameters
                .filter(p => p.risk_level !== "Unknown")
                .map((parameter, index) => (
                  <ParameterCard
                    key={`${parameter.name}-${index}`}
                    name={parameter.name}
                    value={parameter.value}
                    unit={parameter.unit}
                    normalRange={parameter.normal_range}
                    riskLevel={parameter.risk_level as "Normal" | "Mild Abnormal" | "Critical"}
                    explanation={parameter.explanation}
                  />
                ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <p className="text-gray-600">
                No parameters were detected in this report.
              </p>
            </div>
          )}
        </div>

        {/* Lifestyle Recommendations */}
        {uniqueRecommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-semibold text-primary-dark mb-4">
              Lifestyle Recommendations
            </h2>
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
              <p className="text-sm text-blue-900">
                <strong>Note:</strong> These are general suggestions based on your results, not medical advice. 
                Always consult with your healthcare provider before making significant lifestyle changes.
              </p>
            </div>
            <ul className="space-y-3">
              {uniqueRecommendations.map((item, index) => (
                <li key={index} className="flex items-start">
                  <svg
                    className="w-6 h-6 text-primary-medium mr-3 flex-shrink-0 mt-0.5"
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
                  <div>
                    <p className="text-base text-gray-700">
                      {item.recommendation}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Related to: {item.parameter}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Additional Actions */}
        <div className="flex flex-col sm:flex-row gap-4">
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
            Upload Another Report
          </Link>
          {report.parameters && report.parameters.length > 0 && (
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
      </main>
    </div>
  );
}
