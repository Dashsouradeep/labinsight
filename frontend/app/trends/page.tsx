"use client";

import { useTrends } from "@/lib/use-api";
import { useAuth } from "@/lib/use-auth";
import Header from "@/components/Header";
import TrendChart from "@/components/TrendChart";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import { useState } from "react";
import Link from "next/link";

/**
 * TrendsPage Component
 * Displays multi-report trend analysis with charts for each tracked parameter
 * 
 * Features:
 * - Display TrendChart components for each tracked parameter
 * - Show trend direction indicators (Improving, Worsening, Stable)
 * - Display trend summaries
 * - Date range selector for filtering
 * - Medical disclaimer banner
 * 
 * Requirements: 11.7
 */
export default function TrendsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const { trends, isLoading: trendsLoading, isError, error, revalidate } = useTrends();
  const [dateRange, setDateRange] = useState<"all" | "3months" | "6months" | "1year">("all");

  if (authLoading || trendsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary-lighter">
        <LoadingSpinner />
      </div>
    );
  }

  // Filter data points based on selected date range
  const filterDataPointsByDateRange = (dataPoints: any[]) => {
    if (dateRange === "all") return dataPoints;

    const now = new Date();
    const cutoffDate = new Date();

    switch (dateRange) {
      case "3months":
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      case "6months":
        cutoffDate.setMonth(now.getMonth() - 6);
        break;
      case "1year":
        cutoffDate.setFullYear(now.getFullYear() - 1);
        break;
    }

    return dataPoints.filter((point) => new Date(point.date) >= cutoffDate);
  };

  // Get trend direction styling
  const getTrendDirectionStyle = (direction: string) => {
    switch (direction) {
      case "Improving":
        return {
          color: "text-green-600",
          bg: "bg-green-50",
          border: "border-green-200",
          icon: "↑",
        };
      case "Worsening":
        return {
          color: "text-red-600",
          bg: "bg-red-50",
          border: "border-red-200",
          icon: "↓",
        };
      case "Stable":
        return {
          color: "text-blue-600",
          bg: "bg-blue-50",
          border: "border-blue-200",
          icon: "→",
        };
      default:
        return {
          color: "text-gray-600",
          bg: "bg-gray-50",
          border: "border-gray-200",
          icon: "—",
        };
    }
  };

  return (
    <div className="min-h-screen bg-primary-lighter">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-dark mb-2">
            Health Trends Analysis
          </h1>
          <p className="text-gray-600">
            Track how your health parameters change over time across multiple reports.
          </p>
        </div>

        {/* Medical Disclaimer */}
        <div className="mb-8">
          <DisclaimerBanner
            type="general"
            message="This trend analysis is for informational purposes only and is not medical advice. Always consult your doctor for interpretation of your lab results and health trends."
          />
        </div>

        {/* Error Display */}
        {isError && (
          <div className="mb-8">
            <ErrorMessage
              message="Failed to load trend analysis. Please try again."
              onRetry={revalidate}
            />
          </div>
        )}

        {/* No Data State */}
        {!isError && trends && (!trends.parameters || trends.parameters.length === 0) && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
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
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Trend Data Available
            </h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              You need at least 2 completed lab reports to see health trends. Upload more reports to track your health parameters over time.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium shadow-md"
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
              Upload Lab Report
            </Link>
          </div>
        )}

        {/* Trends Content */}
        {!isError && trends && trends.parameters && trends.parameters.length > 0 && (
          <>
            {/* Date Range Selector */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-1">
                    Filter by Date Range
                  </h2>
                  <p className="text-sm text-gray-600">
                    Select a time period to focus your trend analysis
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setDateRange("all")}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      dateRange === "all"
                        ? "bg-primary text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    All Time
                  </button>
                  <button
                    onClick={() => setDateRange("3months")}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      dateRange === "3months"
                        ? "bg-primary text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    3 Months
                  </button>
                  <button
                    onClick={() => setDateRange("6months")}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      dateRange === "6months"
                        ? "bg-primary text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    6 Months
                  </button>
                  <button
                    onClick={() => setDateRange("1year")}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      dateRange === "1year"
                        ? "bg-primary text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    1 Year
                  </button>
                </div>
              </div>
            </div>

            {/* Trend Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-sm text-gray-600 mb-1">Total Parameters</div>
                <div className="text-3xl font-bold text-primary-dark">
                  {trends.parameters.length}
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-sm text-gray-600 mb-1">Improving</div>
                <div className="text-3xl font-bold text-green-600">
                  {trends.parameters.filter((p) => p.trend_direction === "Improving").length}
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-sm text-gray-600 mb-1">Needs Attention</div>
                <div className="text-3xl font-bold text-red-600">
                  {trends.parameters.filter((p) => p.trend_direction === "Worsening").length}
                </div>
              </div>
            </div>

            {/* Trend Charts */}
            <div className="space-y-8">
              {trends.parameters.map((parameterTrend) => {
                const filteredDataPoints = filterDataPointsByDateRange(
                  parameterTrend.data_points
                );

                // Skip if no data points after filtering
                if (filteredDataPoints.length === 0) {
                  return null;
                }

                // Transform data for TrendChart component
                const chartData = filteredDataPoints.map((point) => ({
                  date: point.date,
                  value: point.value,
                  normalRange: {
                    min: parameterTrend.data_points[0].value * 0.8, // Placeholder - should come from backend
                    max: parameterTrend.data_points[0].value * 1.2, // Placeholder - should come from backend
                  },
                }));

                const trendStyle = getTrendDirectionStyle(parameterTrend.trend_direction);

                return (
                  <div key={parameterTrend.parameter_name} className="space-y-4">
                    {/* Trend Summary Card */}
                    <div className="bg-white rounded-lg shadow-md p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-semibold text-gray-900 mb-2">
                            {parameterTrend.parameter_name}
                          </h3>
                          <p className="text-gray-700 mb-3">{parameterTrend.summary}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span>
                              <span className="font-medium">Data Points:</span>{" "}
                              {filteredDataPoints.length} reports
                            </span>
                            {parameterTrend.change_percent !== 0 && (
                              <span>
                                <span className="font-medium">Change:</span>{" "}
                                {parameterTrend.change_percent > 0 ? "+" : ""}
                                {parameterTrend.change_percent.toFixed(1)}%
                              </span>
                            )}
                          </div>
                        </div>
                        <div
                          className={`${trendStyle.bg} ${trendStyle.border} border px-4 py-2 rounded-full flex items-center space-x-2`}
                          aria-label={`Trend: ${parameterTrend.trend_direction}`}
                        >
                          <span className={`text-2xl ${trendStyle.color} font-bold`}>
                            {trendStyle.icon}
                          </span>
                          <span className={`text-sm font-medium ${trendStyle.color}`}>
                            {parameterTrend.trend_direction}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Trend Chart */}
                    <TrendChart
                      parameterName={parameterTrend.parameter_name}
                      dataPoints={chartData}
                    />
                  </div>
                );
              })}
            </div>

            {/* Analysis Timestamp */}
            <div className="mt-8 text-center text-sm text-gray-600">
              Analysis generated on{" "}
              {new Date(trends.generated_at).toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
