"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
  ReferenceLine,
} from 'recharts';

interface TrendChartProps {
  parameterName: string;
  dataPoints: Array<{
    date: string;
    value: number;
    normalRange: { min: number; max: number };
  }>;
}

/**
 * TrendChart Component
 * Displays parameter trends across multiple reports using Recharts
 * Features:
 * - Line chart with data points
 * - Shaded area showing normal range
 * - Trend direction indicator (arrow)
 * - Responsive sizing
 * Requirements: 11.7, 8.6
 */
export default function TrendChart({ parameterName, dataPoints }: TrendChartProps) {
  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-600">No trend data available for {parameterName}</p>
      </div>
    );
  }

  // Calculate trend direction
  const calculateTrendDirection = (): 'improving' | 'worsening' | 'stable' => {
    if (dataPoints.length < 2) return 'stable';

    const latest = dataPoints[dataPoints.length - 1];
    const previous = dataPoints[dataPoints.length - 2];

    // Calculate distance from normal range
    const getDistanceFromNormal = (value: number, range: { min: number; max: number }) => {
      if (value < range.min) return range.min - value;
      if (value > range.max) return value - range.max;
      return 0;
    };

    const latestDistance = getDistanceFromNormal(latest.value, latest.normalRange);
    const previousDistance = getDistanceFromNormal(previous.value, previous.normalRange);

    const change = latestDistance - previousDistance;
    const threshold = latest.normalRange.max * 0.05; // 5% threshold for stability

    if (Math.abs(change) < threshold) return 'stable';
    return change < 0 ? 'improving' : 'worsening';
  };

  const trendDirection = calculateTrendDirection();

  // Prepare chart data
  const chartData = dataPoints.map((point) => ({
    date: new Date(point.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
    value: point.value,
    normalMin: point.normalRange.min,
    normalMax: point.normalRange.max,
  }));

  // Trend indicator styling
  const trendStyles = {
    improving: {
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: '↑',
      label: 'Improving',
    },
    worsening: {
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: '↓',
      label: 'Worsening',
    },
    stable: {
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: '→',
      label: 'Stable',
    },
  };

  const trendStyle = trendStyles[trendDirection];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-medium text-gray-900 mb-1">{data.date}</p>
          <p className="text-sm text-gray-700">
            <span className="font-medium">Value:</span> {data.value}
          </p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">Normal:</span> {data.normalMin} - {data.normalMax}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      {/* Header with parameter name and trend indicator */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{parameterName}</h3>
        <div
          className={`${trendStyle.bg} ${trendStyle.border} border px-3 py-1 rounded-full flex items-center space-x-2`}
          aria-label={`Trend: ${trendStyle.label}`}
        >
          <span className={`text-xl ${trendStyle.color} font-bold`}>
            {trendStyle.icon}
          </span>
          <span className={`text-sm font-medium ${trendStyle.color}`}>
            {trendStyle.label}
          </span>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#9ca3af' }}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            tickLine={{ stroke: '#9ca3af' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '14px', paddingTop: '10px' }}
            iconType="line"
          />

          {/* Normal range as shaded area */}
          <Area
            type="monotone"
            dataKey="normalMax"
            fill="#7AB2B2"
            fillOpacity={0.2}
            stroke="none"
            name="Normal Range"
            legendType="none"
          />
          <Area
            type="monotone"
            dataKey="normalMin"
            fill="#ffffff"
            fillOpacity={1}
            stroke="none"
            legendType="none"
          />

          {/* Reference lines for normal range boundaries */}
          <ReferenceLine
            y={chartData[0].normalMin}
            stroke="#7AB2B2"
            strokeDasharray="5 5"
            strokeWidth={1}
          />
          <ReferenceLine
            y={chartData[0].normalMax}
            stroke="#7AB2B2"
            strokeDasharray="5 5"
            strokeWidth={1}
          />

          {/* Actual value line */}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#088395"
            strokeWidth={3}
            dot={{ fill: '#088395', r: 5 }}
            activeDot={{ r: 7 }}
            name={parameterName}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Data points summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Data Points:</span> {dataPoints.length} reports
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Latest Value:</span>{' '}
          {dataPoints[dataPoints.length - 1].value}
        </p>
      </div>
    </div>
  );
}
