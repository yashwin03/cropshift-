export const getFarmerFriendlyMessage = (code: string | undefined, status?: number): string => {
  switch (code) {
    case 'UNAUTHORIZED':
      return 'Your session has expired. Please sign in again.';
    case 'FORBIDDEN':
      return "You don't have permission to access subsidy information.";
    case 'FARM_NOT_FOUND':
    case 'NOT_FOUND':
      return 'Subsidy information is currently unavailable for this farm.';
    case 'INTERNAL_ERROR':
      return 'CropShift could not load subsidy information right now.';
    case 'NETWORK_ERROR':
      return "CropShift server is unavailable. We couldn't reach the server. Please check that backend service is running.";
    case 'INVALID_FARM':
      return 'Farm information is incomplete. Please check your farm details and try again.';
    case 'FARMER_NOT_FOUND':
      return 'Farmer profile does not exist. Please check your farmer registration.';
    case 'CROP_NOT_FOUND':
      return 'This crop does not exist in our regional registry or has missing reference data.';
    case 'INVALID_INPUT':
      return 'One or more values provided are invalid. Please check your input fields.';
    case 'DATA_UNAVAILABLE':
      return 'No subsidy information is currently available for your region.';
    default:
      if (status === 401) return 'Your session has expired. Please sign in again.';
      if (status === 403) return "You don't have permission to access subsidy information.";
      if (status === 404) return 'Subsidy information is currently unavailable.';
      if (status === 500) return 'CropShift could not load subsidy information right now.';
      return 'An unexpected error occurred. Please try again.';
  }
};
