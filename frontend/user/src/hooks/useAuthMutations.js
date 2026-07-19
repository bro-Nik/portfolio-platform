import { useMutation, useQueryClient } from '@tanstack/react-query';
import { authService } from '@portfolio/shared';

export const useAuthMutations = () => {
  const queryClient = useQueryClient();

  const {
    login: loginApi,
    register: registerApi,
    logout: logoutApi,
    verifyEmail: verifyEmailApi,
    forgotPassword: forgotPasswordApi,
    resetPassword: resetPasswordApi,
    changePassword: changePasswordApi,
    changeEmail: changeEmailApi,
    deleteAccount: deleteAccountApi,
    resendVerification: resendVerificationApi,
    deleteSession: deleteSessionApi,
    logoutAll: logoutAllApi,
  } = authService();

  const login = useMutation({
    mutationFn: ({ email, password }) =>
      loginApi(email, password),
  });

  const register = useMutation({
    mutationFn: ({ email, password }) =>
      registerApi(email, password),
  });

  const logout = useMutation({
    mutationFn: () => logoutApi(),
  });

  const verifyEmail = useMutation({
    mutationFn: (token) => verifyEmailApi(token),
  });

  const forgotPassword = useMutation({
    mutationFn: (email) => forgotPasswordApi(email),
  });

  const resetPassword = useMutation({
    mutationFn: ({ token, password }) =>
      resetPasswordApi(token, password),
  });

  const changePassword = useMutation({
    mutationFn: ({ currentPassword, newPassword }) =>
      changePasswordApi(currentPassword, newPassword),
  });

  const changeEmail = useMutation({
    mutationFn: ({ password, newEmail }) =>
      changeEmailApi(password, newEmail),
  });

  const deleteAccount = useMutation({
    mutationFn: (currentPassword) => deleteAccountApi(currentPassword),
  });

  const resendVerification = useMutation({
    mutationFn: () => resendVerificationApi(),
  });

  const deleteSession = useMutation({
    mutationFn: (sessionId) => deleteSessionApi(sessionId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sessions'] }),
  });

  const logoutAll = useMutation({
    mutationFn: () => logoutAllApi(),
  });

  return {
    login,
    register,
    logout,
    verifyEmail,
    forgotPassword,
    resetPassword,
    changePassword,
    changeEmail,
    deleteAccount,
    resendVerification,
    deleteSession,
    logoutAll,
  };
};
