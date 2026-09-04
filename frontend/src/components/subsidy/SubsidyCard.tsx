import React from 'react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import type { SubsidyScheme } from '../../types/api';
import { getRelevanceLabel, getEligibilityLabel } from '../../utils/labels';

interface SubsidyCardProps {
  scheme: SubsidyScheme;
}

export default function SubsidyCard({ scheme }: SubsidyCardProps) {
  const relevanceLabel = getRelevanceLabel(scheme.relevance);
  const eligibilityLabel = getEligibilityLabel(scheme.eligibility_status);

  // Relevance badge variant mapping
  let relevanceVariant: 'success' | 'warning' | 'neutral' | 'danger' = 'neutral';
  if (scheme.relevance === 'HIGH') {
    relevanceVariant = 'success';
  } else if (scheme.relevance === 'MEDIUM') {
    relevanceVariant = 'warning';
  }

  // Eligibility status formatting/variant mapping
  let eligibilityBg = 'bg-gray-50 border-gray-200 text-gray-700';
  if (scheme.eligibility_status === 'LIKELY_ELIGIBLE') {
    eligibilityBg = 'bg-green-50 border-green-200 text-green-800';
  } else if (scheme.eligibility_status === 'VERIFICATION_REQUIRED') {
    eligibilityBg = 'bg-amber-50 border-amber-200 text-amber-800';
  } else if (scheme.eligibility_status === 'LIKELY_NOT_ELIGIBLE') {
    eligibilityBg = 'bg-red-50 border-red-200 text-red-800';
  }

  return (
    <Card className="border-gray-200 bg-white shadow-sm flex flex-col justify-between">
      <div className="space-y-4">
        {/* Title & Relevance Badge */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-3 border-b border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 leading-tight">
            {scheme.scheme_name}
          </h3>
          <div className="shrink-0">
            <Badge variant={relevanceVariant}>{relevanceLabel}</Badge>
          </div>
        </div>

        {/* Eligibility Status */}
        <div
          data-testid="eligibility-status-banner"
          className={`px-3 py-2 rounded-lg border text-sm font-semibold ${eligibilityBg}`}
        >
          {eligibilityLabel}
        </div>

        {/* Support Information */}
        <div>
          <span className="text-xs text-gray-500 font-medium block">What it Offers</span>
          <p className="text-sm font-bold text-gray-800">{scheme.support_information}</p>
        </div>

        {/* Eligibility Factors */}
        <div>
          <span className="text-xs text-gray-500 font-medium block mb-1">What we checked</span>
          <ul className="list-disc pl-5 text-xs text-gray-600 space-y-1">
            {scheme.eligibility_factors.map((factor, i) => (
              <li key={i}>{factor}</li>
            ))}
          </ul>
        </div>

        {/* Required Information */}
        <div>
          <span className="text-xs text-gray-500 font-medium block mb-1">Documents you need</span>
          <ul className="list-decimal pl-5 text-xs text-gray-600 space-y-1">
            {scheme.required_information.map((doc, i) => (
              <li key={i}>{doc}</li>
            ))}
          </ul>
        </div>

        {/* Verification banner alert */}
        {scheme.verification_required && (
          <div
            data-testid="verification-notice"
            className="bg-amber-50 border border-amber-100 rounded-lg p-3 text-xs text-amber-800 flex items-start gap-2"
          >
            <span aria-hidden="true">⚠️</span>
            <span>
              <strong>Verification Required:</strong> Your actual eligibility must be verified by local officers or via direct application.
            </span>
          </div>
        )}
      </div>

      {/* Source */}
      <div className="text-xs text-gray-400 pt-3 border-t border-gray-50 mt-4">
        Source: {scheme.data_source || 'Government Scheme portal'}
      </div>
    </Card>
  );
}
