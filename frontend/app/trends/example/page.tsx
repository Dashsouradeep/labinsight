"use client";

import TrendChart from "@/components/TrendChart";

/**
 * Example page demonstrating the TrendChart component
 * This shows how the component will be used in the trends page
 */
export default function TrendChartExamplePage() {
  // Example data for Hemoglobin trends
  const hemoglobinData = [
    {
      date: '2024-01-15',
      value: 11.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-02-20',
      value: 12.5,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-03-25',
      value: 13.8,
      normalRange: { min: 12.0, max: 16.0 },
    },
    {
      date: '2024-04-30',
      value: 14.2,
      normalRange: { min: 12.0, max: 16.0 },
    },
  ];

  // Example data for Cholesterol trends
  const cholesterolData = [
    {
      date: '2024-01-15',
      value: 220,
      normalRange: { min: 125, max: 200 },
    },
    {
      date: '2024-02-20',
      value: 215,
      normalRange: { min: 125, max: 200 },
    },
    {
      date: '2024-03-25',
      value: 205,
      normalRange: { min: 125, max: 200 },
    },
    {
      date: '2024-04-30',
      value: 198,
      normalRange: { min: 125, max: 200 },
    },
  ];

  // Example data for Blood Glucose (stable)
  const glucoseData = [
    {
      date: '2024-01-15',
      value: 95,
      normalRange: { min: 70, max: 100 },
    },
    {
      date: '2024-02-20',
      value: 92,
      normalRange: { min: 70, max: 100 },
    },
    {
      date: '2024-03-25',
      value: 94,
      normalRange: { min: 70, max: 100 },
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Health Trends Example
          </h1>
          <p className="text-gray-600">
            Demonstrating the TrendChart component with different trend patterns
          </p>
        </div>

        <div className="space-y-6">
          {/* Improving Trend Example */}
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-3">
              Improving Trend Example
            </h2>
            <TrendChart
              parameterName="Hemoglobin"
              dataPoints={hemoglobinData}
            />
          </div>

          {/* Improving Trend (from above normal) */}
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-3">
              Improving Trend (Cholesterol)
            </h2>
            <TrendChart
              parameterName="Total Cholesterol"
              dataPoints={cholesterolData}
            />
          </div>

          {/* Stable Trend Example */}
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-3">
              Stable Trend Example
            </h2>
            <TrendChart
              parameterName="Blood Glucose"
              dataPoints={glucoseData}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
