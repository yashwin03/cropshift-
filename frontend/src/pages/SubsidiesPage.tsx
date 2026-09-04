import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SubsidyCard from '../components/subsidy/SubsidyCard';
import Spinner from '../components/common/Spinner';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { getFarmDetails } from '../utils/storage';
import { getSubsidies } from '../services/api';
import type { SubsidyScheme } from '../types/api';
import { useApiState } from '../hooks/useApiState';

export default function SubsidiesPage() {
  const navigate = useNavigate();
  const [schemes, setSchemes] = useState<SubsidyScheme[]>([]);
  const farm = getFarmDetails();
  const apiState = useApiState<SubsidyScheme[]>();

  const fetchSubsidies = async () => {
    if (!farm) return;
    const result = await apiState.run(getSubsidies(farm.farm_id));
    if (result) {
      const relevanceWeight = { HIGH: 3, MEDIUM: 2, LOW: 1 };
      const sorted = [...result].sort((a, b) => {
        const weightA = relevanceWeight[a.relevance] || 0;
        const weightB = relevanceWeight[b.relevance] || 0;
        return weightB - weightA;
      });
      setSchemes(sorted);
    }
  };

  useEffect(() => {
    fetchSubsidies();
  }, []);

  const loading = apiState.loading;
  const error = apiState.error;

  if (!farm) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Farm Profile Found"
          message="Please complete your farm details to check for matching government subsidy schemes."
          actionLabel="Go to Farm Analysis"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto py-8">
        <ErrorState message={error} onRetry={fetchSubsidies} />
      </div>
    );
  }

  if (schemes.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4">
        <EmptyState
          title="No Matching Schemes"
          message="No government subsidy schemes were found matching your current farm profile and location."
          actionLabel="Re-Analyze Farm"
          onAction={() => navigate('/analyze')}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="bg-slate-900/90 backdrop-blur-2xl p-5 rounded-3xl border border-slate-800 shadow-2xl flex justify-between items-center">
        <div>
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-400">Government Support Intelligence</div>
          <h1 className="text-2xl font-black text-white leading-tight flex items-center gap-2 mt-0.5">
            <span>📜</span> Smart Subsidy Matcher
          </h1>
        </div>
        <div className="text-xs text-slate-400 font-mono bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
          Matched: <strong className="text-emerald-400">{schemes.length} Schemes</strong>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {schemes.map((scheme) => (
          <SubsidyCard key={scheme.scheme_id} scheme={scheme} />
        ))}
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-xs text-slate-300 flex items-start gap-2.5">
        <span className="text-base" aria-hidden="true">ℹ️</span>
        <div>
          <p className="font-bold text-white mb-0.5">Government Scheme Data Verification</p>
          <p className="text-slate-400">
            Eligibility assessments are based on matching farm profiles and location criteria. A match does not guarantee sanction of the subsidy. All applications must be routed and approved by local department offices.
          </p>
        </div>
      </div>
    </div>
  );
}
