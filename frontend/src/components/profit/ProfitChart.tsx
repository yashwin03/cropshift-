import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import Card from '../common/Card';
import type { ProfitabilityResponse } from '../../types/api';
import { formatINR } from './ProfitComparison';

interface ProfitChartProps {
  data: ProfitabilityResponse;
  className?: string;
}

export default function ProfitChart({ data, className = '' }: ProfitChartProps) {
  const { current_crop, recommended_crop } = data;

  const chartData = [
    {
      category: 'Net Profit',
      [current_crop.crop_name]: current_crop.estimated_profit,
      [recommended_crop.crop_name]: recommended_crop.estimated_profit,
    },
    {
      category: 'Production Cost',
      [current_crop.crop_name]: current_crop.production_cost,
      [recommended_crop.crop_name]: recommended_crop.production_cost,
    },
    {
      category: 'Expected Revenue',
      [current_crop.crop_name]: current_crop.expected_revenue,
      [recommended_crop.crop_name]: recommended_crop.expected_revenue,
    },
  ];

  return (
    <Card className={className}>
      <div className="mb-4">
        <h3 className="text-base font-extrabold text-gray-900 uppercase tracking-wide">
          Financial Comparison Chart
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          Side-by-side visualization of net profit, production costs, and expected revenue per acre (INR).
        </p>
      </div>

      <div data-testid="profit-chart-container" className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 10, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
            <XAxis
              dataKey="category"
              tick={{ fontSize: 12, fill: '#4b5563', fontWeight: 600 }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickFormatter={(val) => `₹${val / 1000}k`}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip
              formatter={(value: number) => [formatINR(value), 'Estimated Amount']}
              contentStyle={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                fontSize: '12px',
              }}
            />
            <Legend
              wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }}
            />
            <Bar
              dataKey={current_crop.crop_name}
              fill="#94a3b8"
              radius={[4, 4, 0, 0]}
              maxBarSize={45}
            />
            <Bar
              dataKey={recommended_crop.crop_name}
              fill="#16a34a"
              radius={[4, 4, 0, 0]}
              maxBarSize={45}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
