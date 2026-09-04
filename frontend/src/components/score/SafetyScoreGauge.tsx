import React from 'react';

interface SafetyScoreGaugeProps {
  score: number;
  size?: number;
  className?: string;
}

export default function SafetyScoreGauge({
  score,
  size = 180,
  className = '',
}: SafetyScoreGaugeProps) {
  // Clamped for visual stroke dash calculation only (display value remains exact score)
  const clampedScore = Math.max(0, Math.min(100, score));

  // Determine color band and accessible rating text
  let strokeColor = '#ef4444'; // Red (0-59)
  let textColor = 'text-red-600';
  let ratingText = 'Low Safety';
  let badgeBg = 'bg-red-100 text-red-800 border-red-200';

  if (score >= 80) {
    strokeColor = '#16a34a'; // Green (80-100)
    textColor = 'text-green-600';
    ratingText = 'High Safety';
    badgeBg = 'bg-green-100 text-green-800 border-green-200';
  } else if (score >= 60) {
    strokeColor = '#f59e0b'; // Amber (60-79)
    textColor = 'text-amber-700';
    ratingText = 'Moderate Safety';
    badgeBg = 'bg-amber-100 text-amber-800 border-amber-200';
  }

  // SVG circular arc dimensions
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  return (
    <div
      data-testid="safety-score-gauge"
      className={`flex flex-col items-center justify-center ${className}`}
    >
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
          aria-label={`Safety score ${score} out of 100, rating: ${ratingText}`}
          role="img"
        >
          {/* Background track circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Active progress circle */}
          <circle
            data-testid="gauge-progress-circle"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-2">
          <span
            data-testid="gauge-score-value"
            className={`text-4xl font-extrabold tracking-tight ${textColor}`}
          >
            {score}
          </span>
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
            out of 100
          </span>
        </div>
      </div>

      {/* Accessible Text Rating Label (independent of color) */}
      <div className="mt-3">
        <span
          data-testid="gauge-rating-label"
          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${badgeBg}`}
        >
          {ratingText}
        </span>
      </div>
    </div>
  );
}
