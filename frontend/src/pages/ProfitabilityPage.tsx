import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';
import LoadingCard from '../components/common/LoadingCard';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import ProfitComparison from '../components/profit/ProfitComparison';
import ProfitChart from '../components/profit/ProfitChart';
import { getProfitability } from '../services/api';
import { getFarmDetails } from '../utils/storage';
import type { ProfitabilityResponse } from '../types/api';

import { useApiState } from '../hooks/useApiState';

export default function ProfitabilityPage() {
  const navigate = useNavigate();
  const farm = getFarmDetails();
  const apiState = useApiState<ProfitabilityResponse>();

  const loadData = async () => {
    if (!farm) return;
    await apiState.run(getProfitability(farm.farm_id));
  };

  useEffect(() => {
    loadData();
  }, []);

  const isLoading = apiState.loading;
  const error = apiState.error;
  const data = apiState.data;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 leading-tight">
            Profitability Comparison
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Side-by-side financial comparison per acre for {farm?.farm_name || 'your farm'}.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate('/recommendation')}
          className="self-start sm:self-center text-xs"
        >
          ← Back to Recommendation
        </Button>
      </div>

      {/* ── Loading State ── */}
      {isLoading && (
        <div data-testid="profitability-loading" className="py-8">
          <LoadingCard message="Calculating crop economics and regional yield comparisons…" />
        </div>
      )}

      {/* ── Error State ── */}
      {!isLoading && error && (
        <ErrorState
          title="Profitability Calculation Failed"
          message={error}
          onRetry={loadData}
        />
      )}

      {/* ── Empty State ── */}
      {!isLoading && !error && !data && (
        <EmptyState
          title="No Profitability Data"
          message="Complete the farm analysis wizard to generate financial estimations."
          actionLabel="Start Farm Analysis"
          onAction={() => navigate('/analyze')}
        />
      )}

      {/* ── Content ── */}
      {!isLoading && !error && data && (
        <>
          <ProfitComparison data={data} />
          <ProfitChart data={data} />

          {/* ── Onward Navigation Footer ── */}
          <div className="pt-6 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-3">
            <Button
              variant="ghost"
              onClick={() => navigate('/recommendation')}
              className="w-full sm:w-auto"
            >
              ← Back to Recommendation
            </Button>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button
                variant="primary"
                onClick={() => navigate('/market')}
                className="w-full sm:w-auto"
              >
                View Market Intelligence →
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
