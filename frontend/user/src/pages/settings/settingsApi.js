import { getAuth } from 'src/api';

const auth = getAuth();

export const settingsApi = {
  getProfile: () => auth.getMeAuthMeGet(),
  /** Выгрузка персональных данных (152-ФЗ, ст. 14). */
  exportData: () => auth.exportAccountAuthAccountExportGet(),
};

/** Скачивает выгрузку как файл, не заходя в сторонние сервисы. */
export const downloadDataExport = async () => {
  const data = await settingsApi.exportData();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `portfolios-data-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  return data;
};
