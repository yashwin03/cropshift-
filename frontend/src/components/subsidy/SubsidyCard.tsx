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

  let relevanceVariant: 'success' | 'warning' | 'neutral' | 'danger' = 'neutral';
  if (scheme.relevance === 'HIGH') {
    relevanceVariant = 'success';
  } else if (scheme.relevance === 'MEDIUM') {
    relevanceVariant = 'warning';
  }

  let eligibilityBg = 'bg-slate-900 border-slate-700 text-slate-300';
  if (scheme.eligibility_status === 'LIKELY_ELIGIBLE') {
    eligibilityBg = 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300';
  } else if (scheme.eligibility_status === 'VERIFICATION_REQUIRED') {
    eligibilityBg = 'bg-amber-950/80 border-amber-500/40 text-amber-300';
  } else if (scheme.eligibility_status === 'LIKELY_NOT_ELIGIBLE') {
    eligibilityBg = 'bg-rose-950/80 border-rose-500/40 text-rose-300';
  }

  const SCHEME_URL_FALLBACKS: Record<string, string> = {
    pm_kisan: 'https://pmkisan.gov.in/',
    pmfby: 'https://pmfby.gov.in/',
    nmeo_os: 'https://nmeo.dac.gov.in/',
    soil_health_card: 'https://soilhealth.dac.gov.in/',
    state_oilseed_support: 'https://fruits.karnataka.gov.in/',
  };

  const isPmKisan = scheme.scheme_id === 'pm_kisan' || scheme.scheme_name.toLowerCase().includes('pm-kisan') || scheme.scheme_name.toLowerCase().includes('pm kisan');
  const officialUrl = scheme.official_url || SCHEME_URL_FALLBACKS[scheme.scheme_id] || (isPmKisan ? 'https://pmkisan.gov.in/' : null);

  const getButtonText = () => {
    if (isPmKisan) return 'Open Official PM-KISAN Portal';
    if (scheme.scheme_id === 'pmfby') return 'Open Official PMFBY Portal';
    if (scheme.scheme_id === 'nmeo_os') return 'Open Official NMEO-OS Portal';
    if (scheme.scheme_id === 'soil_health_card') return 'Open Official Soil Health Portal';
    if (scheme.scheme_id === 'state_oilseed_support') return 'Open Official Karnataka FRUITS Portal';
    return 'Open Official Government Portal';
  };

  return (
    <Card className="border-slate-800 bg-slate-900/90 shadow-xl flex flex-col justify-between p-6 space-y-5">
      <div className="space-y-4">
        {/* Title & Badge */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-3 border-b border-slate-800">
          <h3 className="text-xl font-black text-white leading-tight">
            {scheme.scheme_name}
          </h3>
          <div className="shrink-0">
            <Badge variant={relevanceVariant}>{relevanceLabel}</Badge>
          </div>
        </div>

        {/* Eligibility status */}
        <div
          data-testid="eligibility-status-banner"
          className={`px-3.5 py-2 rounded-xl border text-xs font-bold ${eligibilityBg}`}
        >
          Match Status: {eligibilityLabel}
        </div>

        {/* What it provides */}
        <div>
          <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1">What it provides</span>
          <p className="text-sm font-semibold text-slate-200 leading-relaxed">
            {scheme.support_information}
          </p>
        </div>

        {/* Why CropShift matched it */}
        {scheme.eligibility_factors && scheme.eligibility_factors.length > 0 && (
          <div>
            <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1">Why CropShift matched it</span>
            <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1">
              {scheme.eligibility_factors.map((factor, i) => (
                <li key={i}>{factor}</li>
              ))}
            </ul>
          </div>
        )}

        {/* What the farmer needs */}
        {scheme.required_information && scheme.required_information.length > 0 && (
          <div>
            <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block mb-1">What you need to apply</span>
            <ul className="list-disc pl-5 text-xs text-slate-300 space-y-1">
              {scheme.required_information.map((doc, i) => (
                <li key={i}>{doc}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Simple verification guidance banner */}
        <div
          data-testid="verification-notice"
          className="bg-slate-950/90 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 space-y-1"
        >
          <div className="font-bold text-amber-400 flex items-center gap-1.5">
            <span>ℹ️</span>
            <span>Final Eligibility Confirmation</span>
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Final eligibility must be confirmed through the official government portal or local agricultural officer. CropShift provides automated decision-matching assistance.
          </p>
        </div>
      </div>

      {/* Footer action & source link */}
      <div className="pt-4 border-t border-slate-800 space-y-3 mt-4">
        {officialUrl ? (
          <a
            href={officialUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-slate-950 font-black text-xs rounded-xl shadow-lg shadow-emerald-950/40 transition-all min-h-[44px]"
          >
            <span>🌐</span>
            <span>{getButtonText()}</span>
            <span className="text-xs">↗</span>
          </a>
        ) : (
          <div className="text-[11px] text-slate-500 italic text-center">
            Official source URL unavailable in current dataset
          </div>
        )}

        <div className="text-[10px] text-slate-500 text-center font-mono">
          Source: {scheme.data_source || 'Government Scheme portal'}
        </div>
      </div>
    </Card>
  );
}
