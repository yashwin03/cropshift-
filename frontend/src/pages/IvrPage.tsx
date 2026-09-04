import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import SlideToCall from '../components/ivr/SlideToCall';
import ConnectivityInfo from '../components/ivr/ConnectivityInfo';

const EXOTEL_PHONE_NUMBER = import.meta.env.VITE_EXOTEL_PHONE_NUMBER || '09513886363';
const EXOTEL_PHONE_DISPLAY = import.meta.env.VITE_EXOTEL_PHONE_DISPLAY || '09513886363';
const EXOTEL_PIN = '8618-8551-17';

export default function IvrPage() {
  const [hasTriggeredCall, setHasTriggeredCall] = useState<boolean>(false);

  const handleSlideComplete = () => {
    // 1. Invoke native telephone dialer via tel: URI scheme
    try {
      window.location.href = `tel:${EXOTEL_PHONE_NUMBER}`;
    } catch {
      // In sandbox/desktop environments without a telephony protocol handler
    }
    // 2. Display clear, honest feedback that dialer has been invoked
    setHasTriggeredCall(true);
  };

  const handleReset = () => {
    setHasTriggeredCall(false);
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto pb-8">
      {/* Navigation & Header */}
      <div className="space-y-3">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-600 hover:text-primary-700 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </Link>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse" />
            <span>Works without internet</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 tracking-tight">
            Voice Advisory & Offline Support
          </h1>

          <p className="text-gray-600 text-base md:text-lg max-w-xl font-medium">
            Talk to CropShift over a phone call. Get crop advice through a phone call, even when internet is unavailable.
          </p>
        </div>
      </div>

      {/* Main Slide-to-Call Primary Action Card */}
      <Card className="border-green-200 bg-gradient-to-b from-green-50/50 to-white shadow-sm p-6 md:p-8 space-y-6">
        {!hasTriggeredCall ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <span>📞</span>
                  <span>Get CropShift advice over a phone call</span>
                </h2>
                <span className="text-xs font-mono font-bold bg-green-100 text-green-800 px-3 py-1 rounded-full border border-green-300">
                  PIN: {EXOTEL_PIN}
                </span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                Works through a cellular call to <strong>09513886363</strong> with PIN <strong>8618-8551-17</strong>. Your internet connection is not required during the call.
              </p>
            </div>

            {/* Three Simple Capability Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              {/* Option 1: Crop Recommendation */}
              <div className="p-4 rounded-xl bg-white border border-gray-200 shadow-2xs hover:border-green-300 transition-all space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-green-100 text-green-800 flex items-center justify-center font-bold text-sm">
                  1
                </div>
                <h3 className="font-bold text-gray-900 text-sm">Crop Recommendation</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Get crop guidance through the IVR.
                </p>
              </div>

              {/* Option 2: Market Prices */}
              <div className="p-4 rounded-xl bg-white border border-gray-200 shadow-2xs hover:border-green-300 transition-all space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center font-bold text-sm">
                  2
                </div>
                <h3 className="font-bold text-gray-900 text-sm">Market Prices</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Hear the predefined market-price information.
                </p>
              </div>

              {/* Option 3: Government Schemes */}
              <div className="p-4 rounded-xl bg-white border border-gray-200 shadow-2xs hover:border-green-300 transition-all space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm">
                  3
                </div>
                <h3 className="font-bold text-gray-900 text-sm">Government Schemes</h3>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Hear available demo scheme information.
                </p>
              </div>
            </div>

            {/* Slide to Call Control */}
            <div className="space-y-2 pt-2">
              <SlideToCall
                onSlideComplete={handleSlideComplete}
                label="Slide to Call →"
                activatedLabel="Connecting Phone Dialer..."
              />
              <p className="text-center text-xs font-medium text-gray-500">
                You'll be connected through your phone's normal calling system.
              </p>
            </div>

            {/* Direct fallback helpline link */}
            <div className="pt-3 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3">
              <span className="text-xs text-gray-500">Or tap to dial helpline directly:</span>
              <a
                href={`tel:${EXOTEL_PHONE_NUMBER}`}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold text-primary-800 bg-green-50 hover:bg-green-100 border border-green-200 rounded-xl transition-colors min-h-[44px] w-full sm:w-auto"
              >
                <span aria-hidden="true">📞</span>
                <span>Call {EXOTEL_PHONE_DISPLAY}</span>
              </a>
            </div>
          </div>
        ) : (
          /* Feedback state after sliding */
          <div className="space-y-6 text-center py-2" data-testid="call-triggered-feedback">
            <div className="w-16 h-16 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-3xl mx-auto shadow-sm">
              📞
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900">
                Phone Dialer Triggered
              </h2>
              <p className="text-base text-gray-700 font-semibold">
                Calling: <span className="text-primary-800">{EXOTEL_PHONE_DISPLAY}</span>
              </p>
              <p className="text-xs text-gray-500 max-w-md mx-auto leading-relaxed">
                On your mobile phone, the native dialer has been opened to connect over the cellular network. The voice advisory interaction takes place through the phone network without requiring internet.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <a
                href={`tel:${EXOTEL_PHONE_NUMBER}`}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-bold text-white bg-primary-700 hover:bg-primary-800 rounded-xl shadow transition-colors min-h-[44px] w-full sm:w-auto"
              >
                <span>Dial Again</span>
              </a>
              <Button
                variant="outline"
                onClick={handleReset}
                className="min-h-[44px] w-full sm:w-auto text-sm"
              >
                Reset Control
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Connectivity & Service Status */}
      <ConnectivityInfo />
    </div>
  );
}

