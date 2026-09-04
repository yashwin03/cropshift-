import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { saveFarmDetails, saveRecommendation } from '../utils/storage';
import type { FarmDetails } from '../mocks/fixtures';
import { getRecommendation, createFarm } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { IconMapPin, IconCheck, IconSparkles } from '../components/common/Icons';

/* ─── Constants ──────────────────────────────────────────────────────────── */

const CROP_OPTIONS = [
  'Paddy', 'Maize', 'Groundnut', 'Sunflower', 'Soybean', 'Mustard', 'Sesame'
];

const WATER_OPTIONS: FarmDetails['water_availability'][] = [
  'Available', 'Limited', 'Scarce',
];

const SOIL_OPTIONS = [
  'Clayey', 'Sandy', 'Loamy', 'Black (Vertisol)', 'Red Laterite', 'Alluvial',
];

const TOTAL_STEPS = 4;

/* ─── Form state shape ───────────────────────────────────────────────────── */

interface FormValues {
  farm_name: string;
  land_area: string;           // keep as string for input control
  current_crop: string;
  water_availability: FarmDetails['water_availability'] | '';
  soil_type: string;
  district: string;
  state: string;
  latitude: string;
  longitude: string;
}

interface FormErrors {
  farm_name?: string;
  land_area?: string;
  current_crop?: string;
  water_availability?: string;
}

/* ─── Sub-components ─────────────────────────────────────────────────────── */

function ProgressIndicator({ step }: { step: number }) {
  const steps = [
    { num: '01', label: 'General Info', sublabel: 'Farm & area' },
    { num: '02', label: 'Current Crop', sublabel: 'What you grow' },
    { num: '03', label: 'Conditions', sublabel: 'Soil & water' },
    { num: '04', label: 'Analyze', sublabel: 'AI recommendation' },
  ];

  return (
    <div className="mb-8">
      <div className="flex items-center gap-0">
        {steps.map((s, i) => {
          const isCompleted = i + 1 < step;
          const isActive = i + 1 === step;
          return (
            <React.Fragment key={s.num}>
              <div className="flex flex-col items-center min-w-0" style={{ flex: 1 }}>
                {/* Circle */}
                <div
                  className={`w-10 h-10 rounded-full border-2 flex items-center justify-center font-black text-xs transition-all duration-300 ${
                    isCompleted
                      ? 'bg-emerald-500 border-emerald-500 text-white shadow-md shadow-emerald-500/30'
                      : isActive
                      ? 'bg-amber-500 border-amber-500 text-slate-950 shadow-md shadow-amber-500/40 scale-110'
                      : 'bg-slate-900 border-slate-700 text-slate-500'
                  }`}
                >
                  {isCompleted ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  ) : (
                    <span>{s.num}</span>
                  )}
                </div>
                {/* Labels */}
                <div className="text-center mt-1.5 hidden sm:block">
                  <div className={`text-[10px] font-black uppercase tracking-wide ${
                    isActive ? 'text-amber-400' : isCompleted ? 'text-emerald-400' : 'text-slate-500'
                  }`}>{s.label}</div>
                  <div className="text-[9px] text-slate-600">{s.sublabel}</div>
                </div>
              </div>
              {/* Connector line */}
              {i < steps.length - 1 && (
                <div
                  className={`h-0.5 transition-all duration-500 ${
                    i + 1 < step ? 'bg-emerald-500' : 'bg-slate-800'
                  }`}
                  style={{ flex: 0.5 }}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
      {/* Active step label for mobile */}
      <p className="mt-3 text-xs font-bold text-slate-400 text-center sm:hidden">
        Step {step} of {TOTAL_STEPS}: {steps[step - 1].label}
      </p>
    </div>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return (
    <p role="alert" className="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
      <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
      {message}
    </p>
  );
}

function InputLabel({
  htmlFor,
  children,
  optional = false,
}: {
  htmlFor: string;
  children: React.ReactNode;
  optional?: boolean;
}) {
  return (
    <label htmlFor={htmlFor} className="block text-sm font-bold text-gray-700 mb-1.5">
      {children}
      {optional && (
        <span className="ml-2 text-xs font-normal text-gray-400">(Optional)</span>
      )}
    </label>
  );
}

const inputClass =
  'w-full rounded-lg border border-gray-300 px-4 py-3 text-base text-gray-900 ' +
  'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ' +
  'disabled:bg-gray-100 min-h-[44px]';

const selectClass = inputClass + ' bg-white';

/* ─── Step 1: Farm General Info ──────────────────────────────────────────── */

function StepGeneralInfo({
  values,
  errors,
  onChange,
}: {
  values: FormValues;
  errors: FormErrors;
  onChange: (field: keyof FormValues, value: string) => void;
}) {
  return (
    <div className="space-y-6">
      <div>
        <InputLabel htmlFor="farm_name">Farm Name or ID</InputLabel>
        <input
          id="farm_name"
          type="text"
          value={values.farm_name}
          onChange={e => onChange('farm_name', e.target.value)}
          placeholder="e.g. Green Field Farm"
          className={inputClass}
          autoComplete="off"
        />
        <FieldError message={errors.farm_name} />
      </div>

      <div>
        <InputLabel htmlFor="land_area">Land Area (Acres)</InputLabel>
        <input
          id="land_area"
          type="text"
          inputMode="decimal"
          value={values.land_area}
          onChange={e => onChange('land_area', e.target.value)}
          placeholder="e.g. 2.5"
          className={inputClass}
          autoComplete="off"
        />
        <FieldError message={errors.land_area} />
        <p className="mt-1.5 text-xs text-gray-500">Enter total cultivable area in acres (max 1,000 acres).</p>
      </div>
    </div>
  );
}

/* ─── Step 2: Crop Selection ─────────────────────────────────────────────── */

function StepCropSelection({
  values,
  errors,
  onChange,
}: {
  values: FormValues;
  errors: FormErrors;
  onChange: (field: keyof FormValues, value: string) => void;
}) {
  return (
    <div className="space-y-6">
      <div>
        <InputLabel htmlFor="current_crop">What crop are you growing now?</InputLabel>
        <select
          id="current_crop"
          value={values.current_crop}
          onChange={e => onChange('current_crop', e.target.value)}
          className={selectClass}
        >
          <option value="">— Select a crop —</option>
          {CROP_OPTIONS.map(crop => (
            <option key={crop} value={crop}>{crop}</option>
          ))}
        </select>
        <FieldError message={errors.current_crop} />
      </div>

      {values.current_crop && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800 font-medium">
          You selected: <strong>{values.current_crop}</strong>. We will compare this against suitable oilseed alternatives.
        </div>
      )}
    </div>
  );
}

/* ─── Step 3: Farm Conditions ────────────────────────────────────────────── */

function StepFarmConditions({
  values,
  errors,
  onChange,
}: {
  values: FormValues;
  errors: FormErrors;
  onChange: (field: keyof FormValues, value: string) => void;
}) {
  return (
    <div className="space-y-6">
      {/* Water Availability — required */}
      <div>
        <InputLabel htmlFor="water_availability">Water Availability</InputLabel>
        <div className="grid grid-cols-3 gap-3">
          {WATER_OPTIONS.map(opt => (
            <button
              key={opt}
              type="button"
              onClick={() => onChange('water_availability', opt)}
              className={`min-h-[48px] rounded-xl border-2 px-3 py-2.5 text-sm font-bold transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 ${
                values.water_availability === opt
                  ? opt === 'Available'
                    ? 'border-emerald-500 bg-emerald-950 text-emerald-300 shadow-md shadow-emerald-500/20'
                    : opt === 'Limited'
                    ? 'border-amber-500 bg-amber-950 text-amber-300 shadow-md shadow-amber-500/20'
                    : 'border-rose-500 bg-rose-950 text-rose-300 shadow-md shadow-rose-500/20'
                  : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'
              }`}
            >
              {opt === 'Available' ? 'Available' : opt === 'Limited' ? 'Limited' : 'Scarce'}
            </button>
          ))}
        </div>
        <FieldError message={errors.water_availability} />
      </div>

      {/* Soil Type — optional */}
      <div>
        <InputLabel htmlFor="soil_type" optional>Soil Type</InputLabel>
        <select
          id="soil_type"
          value={values.soil_type}
          onChange={e => onChange('soil_type', e.target.value)}
          className={selectClass}
        >
          <option value="">— Select soil type (optional) —</option>
          {SOIL_OPTIONS.map(soil => (
            <option key={soil} value={soil}>{soil}</option>
          ))}
        </select>
        <p className="mt-1.5 text-xs text-gray-500">
          Optional. We'll use regional averages if you skip this.
        </p>
      </div>

      {/* Location — optional */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <InputLabel htmlFor="district" optional>Location Details</InputLabel>
          <Button 
            variant="primary" 
            size="sm" 
            className="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-black shadow-md border border-amber-400 min-h-[38px] px-3 flex items-center gap-1.5"
            onClick={() => {
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                  (position) => {
                    onChange('latitude', position.coords.latitude.toFixed(6));
                    onChange('longitude', position.coords.longitude.toFixed(6));
                  },
                  (error) => {
                    alert('Unable to retrieve your location. Please enter manually.');
                  }
                );
              } else {
                alert('Geolocation is not supported by this browser.');
              }
            }}
            type="button"
          >
            <IconMapPin size={14} className="text-slate-950" />
            <span>Use My Current Location</span>
          </Button>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="district" className="block text-xs font-medium text-gray-500 mb-1">District</label>
            <input
              id="district"
              type="text"
              value={values.district}
              onChange={e => onChange('district', e.target.value)}
              placeholder="e.g. Guntur"
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="state" className="block text-xs font-medium text-gray-500 mb-1">State</label>
            <input
              id="state"
              type="text"
              value={values.state}
              onChange={e => onChange('state', e.target.value)}
              placeholder="e.g. Andhra Pradesh"
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="latitude" className="block text-xs font-medium text-gray-500 mb-1">Latitude</label>
            <input
              id="latitude"
              type="text"
              value={values.latitude}
              onChange={e => onChange('latitude', e.target.value)}
              placeholder="e.g. 16.306"
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="longitude" className="block text-xs font-medium text-gray-500 mb-1">Longitude</label>
            <input
              id="longitude"
              type="text"
              value={values.longitude}
              onChange={e => onChange('longitude', e.target.value)}
              placeholder="e.g. 80.436"
              className={inputClass}
            />
          </div>
        </div>
        {(!values.latitude || !values.longitude) && (
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 font-medium">
            ⚠️ Without exact GPS coordinates, market distance estimates will be less accurate.
          </p>
        )}
      </div>
    </div>
  );
}

/* ─── Step 4: Review & Analyze ───────────────────────────────────────────── */

function StepReview({
  values,
  isSubmitting,
  submitError,
  onSubmit,
}: {
  values: FormValues;
  isSubmitting: boolean;
  submitError: string | null;
  onSubmit: () => void;
}) {
  const rows: { label: string; value: string; emphasis?: boolean }[] = [
    { label: 'Farm Name', value: values.farm_name },
    { label: 'Land Area', value: `${values.land_area} acres` },
    { label: 'Current Crop', value: values.current_crop },
    { label: 'Water Availability', value: values.water_availability || '—', emphasis: true },
    { label: 'Soil Type', value: values.soil_type || 'Not specified (regional average will be used)' },
    { label: 'Location', value: values.district && values.state ? `${values.district}, ${values.state}` : 'Not specified' },
    { label: 'GPS', value: values.latitude && values.longitude ? `${values.latitude}, ${values.longitude}` : 'Not specified' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-gray-50 border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <tbody>
            {rows.map(({ label, value, emphasis }) => (
              <tr key={label} className="border-b border-gray-100 last:border-0">
                <td className="px-4 py-3 font-semibold text-gray-500 whitespace-nowrap w-1/3">{label}</td>
                <td className={`px-4 py-3 font-medium ${emphasis ? 'text-primary font-bold' : 'text-gray-900'}`}>
                  {value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-primary-50 border border-primary-200 rounded-xl p-4 text-sm text-primary-900">
        <p className="font-bold mb-1">Ready to analyze?</p>
        <p>
          Our decision engine will check crop suitability, expected profitability, local market conditions, and
          risks to give you a clear recommendation.
        </p>
      </div>

      {submitError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-800 space-y-2">
          <p className="font-bold">Analysis Failed</p>
          <p>{submitError}</p>
          {submitError.toLowerCase().includes('log in') && (
            <div className="pt-2">
              <a
                href="/login"
                className="inline-flex items-center gap-1 font-bold text-primary-800 bg-white px-3 py-1.5 rounded-lg border border-red-300 shadow-sm hover:bg-gray-50 text-xs"
              >
                <span>🔑 Go to Login Page</span>
              </a>
            </div>
          )}
        </div>
      )}

      <Button
        variant="primary"
        onClick={onSubmit}
        isLoading={isSubmitting}
        className="w-full text-lg py-4 shadow-md font-black bg-emerald-600 hover:bg-emerald-500"
      >
        {isSubmitting ? 'Analyzing…' : 'Analyze My Farm'}
      </Button>
    </div>
  );
}

/* ─── Validation ─────────────────────────────────────────────────────────── */

function validateStep(step: number, values: FormValues): FormErrors {
  const errors: FormErrors = {};

  if (step === 1) {
    if (!values.farm_name.trim()) {
      errors.farm_name = 'Please enter your farm name or ID.';
    }
    const area = parseFloat(values.land_area);
    if (!values.land_area.trim()) {
      errors.land_area = 'Please enter your land area in acres.';
    } else if (isNaN(area) || area <= 0) {
      errors.land_area = 'Land area must be a number greater than zero.';
    } else if (area > 1000) {
      errors.land_area = 'Land area cannot exceed 1,000 acres. Please check the value you entered.';
    }
  }

  if (step === 2) {
    if (!values.current_crop) {
      errors.current_crop = 'Please select your current crop.';
    }
  }

  if (step === 3) {
    if (!values.water_availability) {
      errors.water_availability = 'Please select your water availability level.';
    }
  }

  return errors;
}

/* ─── Main Page ──────────────────────────────────────────────────────────── */

const INITIAL_FORM: FormValues = {
  farm_name: '',
  land_area: '',
  current_crop: '',
  water_availability: '',
  soil_type: '',
  district: '',
  state: '',
  latitude: '',
  longitude: '',
};

export default function FarmInfoPage() {
  const navigate = useNavigate();
  let user: any = null;
  try {
    const auth = useAuth();
    user = auth?.user;
  } catch {
    // Fallback if rendered outside AuthProvider in standalone unit tests
  }

  const [step, setStep] = useState(1);
  const [values, setValues] = useState<FormValues>(INITIAL_FORM);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.username && !values.farm_name) {
      setValues((prev) => ({
        ...prev,
        farm_name: `${user.username}'s Farm`,
      }));
    }
  }, [user]);

  const handleChange = (field: keyof FormValues, value: string) => {
    setValues(prev => ({ ...prev, [field]: value }));
    // Clear error on change
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleNext = () => {
    const stepErrors = validateStep(step, values);
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }
    setErrors({});
    setStep(s => s + 1);
  };

  const handleBack = () => {
    setErrors({});
    setStep(s => s - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    // Build persisted farm record
    const farmRecord: FarmDetails = {
      farm_id: 0,
      farm_name: values.farm_name.trim(),
      land_area: parseFloat(values.land_area),
      current_crop: values.current_crop,
      water_availability: values.water_availability as FarmDetails['water_availability'],
      soil_type: values.soil_type || undefined,
      district: values.district.trim() || 'Not specified',
      state: values.state.trim() || 'Not specified',
      latitude: values.latitude ? parseFloat(values.latitude) : undefined,
      longitude: values.longitude ? parseFloat(values.longitude) : undefined,
    };

    try {
      // 1. Persist the Farm to the backend
      const farmPayload = {
        farm_name: values.farm_name.trim() || undefined,
        land_area_acre: parseFloat(values.land_area),
        water_availability: values.water_availability === 'Available', // Map string to boolean based on your model if needed, but the model expects boolean. Wait, backend models expects bool: True for Available, False for Limited/Scarce
        soil_type: values.soil_type || undefined,
        district: values.district.trim() || undefined,
        state: values.state.trim() || undefined,
        current_crop: values.current_crop,
        latitude: values.latitude ? parseFloat(values.latitude) : undefined,
        longitude: values.longitude ? parseFloat(values.longitude) : undefined,
      };

      // Ensure we map 'Available' to true, and others to false based on schema
      farmPayload.water_availability = (values.water_availability === 'Available');

      const savedFarm = await createFarm(farmPayload);
      
      // Update our local record with the real farm_id
      farmRecord.farm_id = savedFarm.id;

      // 2. Delegate to recommendation service
      const recommendation = await getRecommendation(farmRecord);
      
      saveFarmDetails(farmRecord);
      saveRecommendation(recommendation);
      navigate('/recommendation');
    } catch (err: any) {
      if (err.code === 'CLIENT_ERROR' || err.code === 'VALIDATION_ERROR' || err.code === 'INVALID_INPUT' || err.code === 'FARM_NOT_FOUND') {
        setSubmitError(err.message || "Some farm details were invalid. Please check your information and try again.");
      } else if (err.code === 'UNAUTHORIZED' || err.code === 'FORBIDDEN') {
        setSubmitError(err.message || "You must be logged in to analyze and save your farm. Please log in first.");
      } else if (err.code === 'NETWORK_ERROR') {
        setSubmitError("Could not reach the server. Please check your connection and make sure the backend is running.");
      } else {
        setSubmitError("We couldn't analyze your farm right now. An unexpected error occurred.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const stepTitles = [
    'Tell us about your farm',
    'What are you currently growing?',
    'Describe your farming conditions',
    'Review your information',
  ];

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-gray-900 leading-tight">
          {stepTitles[step - 1]}
        </h1>
        <p className="text-gray-500 mt-1 text-sm">
          We need a few details to give you the most accurate crop recommendation.
        </p>
      </div>

      <ProgressIndicator step={step} />

      <Card>
        {step === 1 && (
          <StepGeneralInfo values={values} errors={errors} onChange={handleChange} />
        )}
        {step === 2 && (
          <StepCropSelection values={values} errors={errors} onChange={handleChange} />
        )}
        {step === 3 && (
          <StepFarmConditions values={values} errors={errors} onChange={handleChange} />
        )}
        {step === 4 && (
          <StepReview 
            values={values} 
            isSubmitting={isSubmitting} 
            submitError={submitError} 
            onSubmit={handleSubmit} 
          />
        )}

        {/* Navigation Buttons */}
        {step < 4 && (
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            {step > 1 ? (
              <Button variant="ghost" onClick={handleBack} className="min-h-[44px]">
                ← Back
              </Button>
            ) : (
              <div /> /* spacer */
            )}
            <Button variant="primary" onClick={handleNext} className="min-h-[44px] px-8">
              {step === 3 ? 'Review →' : 'Next →'}
            </Button>
          </div>
        )}

        {/* Back button on review step */}
        {step === 4 && (
          <div className="mt-4 flex justify-start">
            <Button variant="ghost" onClick={handleBack} className="text-sm min-h-[44px]">
              ← Edit Details
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
