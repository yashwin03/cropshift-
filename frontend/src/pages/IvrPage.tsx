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
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-300 hover:text-emerald-400 transition-colors"
        >
          <span>←</span> Back to Dashboard
        </Link>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-bold uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Works without internet</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Voice Advisory & Offline Support
          </h1>

          <p className="text-slate-300 text-base md:text-lg max-w-xl font-medium">
            Talk to CropShift over a phone call. Get crop advice through a phone call, even when internet is unavailable.
          </p>
        </div>
      </div>

      {/* Main Slide-to-Call Primary Action Card */}
      <Card className="border-emerald-500/30 bg-slate-900/90 shadow-2xl p-6 md:p-8 space-y-6">
        {!hasTriggeredCall ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>📞</span>
                  <span>Get CropShift advice over a phone call</span>
                </h2>
                <span className="text-xs font-mono font-bold bg-amber-950 text-amber-300 px-3 py-1 rounded-full border border-amber-500/40">
                  PIN: {EXOTEL_PIN}
                </span>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed">
                Works through a cellular call to <strong className="text-emerald-400 font-mono">09513886363</strong> with PIN <strong className="text-amber-400 font-mono">8618-8551-17</strong>. Your internet connection is not required during the call.
              </p>
            </div>

            {/* Six IVR Capability Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
              {/* Option 1: Crop Recommendation */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-sm">
                  1
                </div>
                <h3 className="font-bold text-white text-sm">Crop Recommendation</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Hear tailored oilseed recommendation (Groundnut / Castor scenarios).
                </p>
              </div>

              {/* Option 2: Weather Report */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-sky-950 text-sky-400 border border-sky-500/30 flex items-center justify-center font-bold text-sm">
                  2
                </div>
                <h3 className="font-bold text-white text-sm">Weather Report</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Regional weather advisory for rainfall and temperature.
                </p>
              </div>

              {/* Option 3: Mandi / Market Prices */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-blue-950 text-blue-400 border border-blue-500/30 flex items-center justify-center font-bold text-sm">
                  3
                </div>
                <h3 className="font-bold text-white text-sm">Mandi & Market Prices</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  APMC modal, minimum, and maximum commodity prices.
                </p>
              </div>

              {/* Option 4: Government Schemes */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-amber-950 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold text-sm">
                  4
                </div>
                <h3 className="font-bold text-white text-sm">Government Schemes</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  PM-KISAN, Soil Health Card, and oilseed subsidy guidance.
                </p>
              </div>

              {/* Option 5: Crop Growing Advisory */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-purple-950 text-purple-400 border border-purple-500/30 flex items-center justify-center font-bold text-sm">
                  5
                </div>
                <h3 className="font-bold text-white text-sm">Farm Advisory</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Irrigation, soil nutrient, and crop protection guidance.
                </p>
              </div>

              {/* Option 6: Repeat Main Menu */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center font-bold text-sm">
                  6
                </div>
                <h3 className="font-bold text-white text-sm">Repeat Menu</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Re-play main menu voice prompt options.
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
              <p className="text-center text-xs font-medium text-slate-300">
                You'll be connected through your phone's normal calling system.
              </p>
            </div>

            {/* Direct fallback helpline link */}
            <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
              <span className="text-xs text-slate-300">Or tap to dial helpline directly:</span>
              <a
                href={`tel:${EXOTEL_PHONE_NUMBER}`}
                className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition-colors min-h-[44px] w-full sm:w-auto"
              >
                <span aria-hidden="true">📞</span>
                <span>Call {EXOTEL_PHONE_DISPLAY}</span>
              </a>
            </div>
          </div>
        ) : (
          /* Feedback state after sliding */
          <div className="space-y-6 text-center py-2" data-testid="call-triggered-feedback">
            <div className="w-16 h-16 bg-emerald-950 text-emerald-400 border border-emerald-500/40 rounded-full flex items-center justify-center text-3xl mx-auto shadow-sm">
              📞
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-white">
                Phone Dialer Triggered
              </h2>
              <p className="text-base text-slate-200 font-semibold">
                Calling: <span className="text-emerald-400 font-mono">{EXOTEL_PHONE_DISPLAY}</span>
              </p>
              <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
                On your mobile phone, the native dialer has been opened to connect over the cellular network. The voice advisory interaction takes place through the phone network without requiring internet.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <a
                href={`tel:${EXOTEL_PHONE_NUMBER}`}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl shadow transition-colors min-h-[44px] w-full sm:w-auto"
              >
                <span>Dial Again</span>
              </a>
              <Button
                variant="outline"
                onClick={handleReset}
                className="min-h-[44px] w-full sm:w-auto text-sm bg-slate-950 text-slate-200 border-slate-700 hover:bg-slate-800"
              >
                Reset Control
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
