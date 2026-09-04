import React, { useState, useRef, useEffect, useCallback } from 'react';

interface SlideToCallProps {
  onSlideComplete: () => void;
  disabled?: boolean;
  isActivated?: boolean;
  label?: string;
  activatedLabel?: string;
}

export default function SlideToCall({
  onSlideComplete,
  disabled = false,
  isActivated = false,
  label = 'Slide to activate IVR advice',
  activatedLabel = 'IVR Connected',
}: SlideToCallProps) {
  const [sliderPosition, setSliderPosition] = useState(0); // 0 to 100
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const thumbRef = useRef<HTMLDivElement>(null);

  const handleComplete = useCallback(() => {
    setSliderPosition(100);
    onSlideComplete();
  }, [onSlideComplete]);

  // Reset slider if isActivated becomes false
  useEffect(() => {
    if (!isActivated) {
      setSliderPosition(0);
    } else {
      setSliderPosition(100);
    }
  }, [isActivated]);

  const updatePosition = useCallback((clientX: number) => {
    if (!containerRef.current || isActivated || disabled) return;
    const rect = containerRef.current.getBoundingClientRect();
    const thumbWidth = thumbRef.current ? thumbRef.current.offsetWidth : 48;
    const maxDistance = rect.width - thumbWidth;
    if (maxDistance <= 0) return;

    const currentX = clientX - rect.left - thumbWidth / 2;
    const percentage = Math.min(Math.max((currentX / maxDistance) * 100, 0), 100);
    setSliderPosition(percentage);

    if (percentage >= 90) {
      setIsDragging(false);
      handleComplete();
    }
  }, [isActivated, disabled, handleComplete]);

  // Mouse event handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (disabled || isActivated) return;
    setIsDragging(true);
    updatePosition(e.clientX);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        updatePosition(e.clientX);
      }
    };

    const handleMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
        if (sliderPosition < 90) {
          setSliderPosition(0);
        }
      }
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, sliderPosition, updatePosition]);

  // Touch event handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled || isActivated) return;
    setIsDragging(true);
    updatePosition(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (isDragging) {
      updatePosition(e.touches[0].clientX);
    }
  };

  const handleTouchEnd = () => {
    if (isDragging) {
      setIsDragging(false);
      if (sliderPosition < 90) {
        setSliderPosition(0);
      }
    }
  };

  // Keyboard accessibility
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled || isActivated) return;
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter' || e.key === 'End') {
      e.preventDefault();
      handleComplete();
    } else if (e.key === 'ArrowLeft' || e.key === 'Home') {
      e.preventDefault();
      setSliderPosition(0);
    }
  };

  return (
    <div
      ref={containerRef}
      data-testid="slide-to-call-container"
      role="slider"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(sliderPosition)}
      tabIndex={disabled || isActivated ? -1 : 0}
      onKeyDown={handleKeyDown}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className={`relative w-full h-14 rounded-full overflow-hidden select-none cursor-pointer transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 ${
        isActivated
          ? 'bg-green-600 text-white'
          : disabled
          ? 'bg-gray-200 cursor-not-allowed opacity-60'
          : 'bg-gradient-to-r from-primary-700 via-primary-600 to-green-600 border border-primary-700 shadow-md'
      }`}
    >
      {/* Background slide fill */}
      <div
        className="absolute inset-y-0 left-0 bg-green-500/40 transition-all duration-75"
        style={{ width: `${sliderPosition}%` }}
      />

      {/* Label text */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none px-12">
        <span className="text-white text-sm md:text-base font-bold tracking-wide flex items-center gap-2 drop-shadow-sm">
          {isActivated ? (
            <>
              <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
              {activatedLabel}
            </>
          ) : (
            <>
              <span>{label}</span>
              <span className="animate-pulse hidden sm:inline">&rarr;&rarr;&rarr;</span>
            </>
          )}
        </span>
      </div>

      {/* Sliding Thumb Button */}
      {!isActivated && (
        <div
          ref={thumbRef}
          data-testid="slide-thumb"
          className={`absolute top-1 left-1 bottom-1 w-12 rounded-full bg-white shadow-lg flex items-center justify-center text-primary-700 font-extrabold text-xl transition-all duration-75 ${
            isDragging ? 'scale-105 shadow-xl' : 'hover:bg-gray-50'
          }`}
          style={{
            transform: `translateX(${(sliderPosition / 100) * ((containerRef.current?.offsetWidth || 300) - 56)}px)`,
          }}
        >
          <span aria-hidden="true">📞</span>
        </div>
      )}
    </div>
  );
}
