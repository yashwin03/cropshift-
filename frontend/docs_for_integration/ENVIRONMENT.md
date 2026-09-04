
# Environment Variables Configuration

This document describes the environment variables required for running and integrating the CropShift frontend.

## Environment Variables

### 1. VITE_API_BASE_URL
- **Description**: The base HTTP URL where the CropShift backend is hosting its API endpoints.
- **Type**: String URL (no trailing slash).
- **Default Value (Development)**: http://localhost:8000 (or the backend developer's local dev server URL).
- **Example Usage**: VITE_API_BASE_URL=http://localhost:8000

### 2. VITE_USE_MOCKS
- **Description**: A boolean flag to toggle the API client between using local mock datasets or calling real backend HTTP endpoints.
- **Type**: String (	rue or alse).
- **Default Value (Mocks enabled)**: 	rue (renders all pages, charts, map markers, IVR flows using isolated, deterministic frontend data).
- **Default Value (Integration)**: alse (forces API client to make real etch network requests to VITE_API_BASE_URL).
- **Example Usage**: VITE_USE_MOCKS=false

## Working Example (.env)
Create a .env file in the rontend/ root:
`env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=true
`
During final integration, change to:
`env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCKS=false
`
