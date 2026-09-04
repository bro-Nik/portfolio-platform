import { getAuth } from 'src/api';

const auth = getAuth();

export const settingsApi = {
  getProfile: () => auth.getMeAuthMeGet(),
};
