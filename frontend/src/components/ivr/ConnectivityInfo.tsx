import React, { useState, useEffect } from 'react';
import Card from '../common/Card';

export default function ConnectivityInfo() {
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <Card className="border-gray-200 bg-white" data-testid="connectivity-info">
      <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-base" aria-hidden="true">📡</span>
          <h3 className="text-sm font-bold text-gray-900">Internet Connection & Service Status</h3>
        </div>
        <div
          className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${
            isOnline ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
          }`}
          role="status"
          aria-live="polite"
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isOnline ? 'bg-green-600' : 'bg-amber-600 animate-pulse'
            }`}
          />
          <span>{isOnline ? 'Connected' : 'No internet connection'}</span>
        </div>
      </div>

      <p className="text-xs text-gray-600 mb-3 leading-relaxed">
        The CropShift app can open without internet, but cloud analysis features require connectivity. Voice Advisory works anytime through your phone line:
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        {/* Available without internet */}
        <div className="p-3 rounded-xl bg-green-50/70 border border-green-200 space-y-2">
          <div className="flex items-center gap-1.5 font-bold text-green-900">
            <span className="text-green-700">✓</span>
            <span>AVAILABLE WITHOUT INTERNET</span>
          </div>
          <ul className="space-y-1.5 text-gray-700 pl-4 list-disc list-outside">
            <li>
              <strong className="text-green-900">Voice Advisory by phone</strong>
              <div className="text-[11px] text-gray-600">Cellular call to 09513886363 with PIN 8618-8551-17</div>
            </li>
          </ul>
        </div>

        {/* Requires internet */}
        <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-200 space-y-2">
          <div className="flex items-center gap-1.5 font-bold text-blue-900">
            <span className="w-2 h-2 rounded-full bg-blue-600" />
            <span>REQUIRES INTERNET</span>
          </div>
          <ul className="space-y-1 text-gray-700 pl-4 list-disc list-outside">
            <li>Crop recommendation calculations</li>
            <li>Live APMC market prices</li>
            <li>Map / geospatial routing</li>
            <li>Government subsidy information</li>
            <li>Risk simulation scenarios</li>
            <li>Other cloud API features</li>
          </ul>
        </div>
      </div>
    </Card>
  );
}
