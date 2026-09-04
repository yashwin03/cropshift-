
# Frontend Setup Guide

This document describes the instructions to set up, run, build, and test the CropShift frontend application.

## Prerequisites
- Node.js (v18 or higher recommended)
- npm (installed with Node)

## Commands

### 1. Installation
Install dependencies in the frontend workspace:
`ash
npm install
`

### 2. Development Mode
Run the local Vite development server:
`ash
npm run dev
`

### 3. Production Build
Type check and build the production bundle:
`ash
npm run build
`
This builds and places the minified static build files under dist/.

### 4. Tests
Run the Vitest suite in single run mode:
`ash
npm test -- --run
`
To run the type-checker:
`ash
npx tsc --noEmit
`

