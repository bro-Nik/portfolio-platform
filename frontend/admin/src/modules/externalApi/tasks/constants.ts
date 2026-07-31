export interface SchedulePreset {
  value: string;
  label: string;
}

export const schedulePresets: SchedulePreset[] = [
  { value: '', label: 'Запуск вручную' },
  { value: '*/15 * * * *', label: 'Раз в 15 минут' },
  { value: '0 * * * *', label: 'Раз в час' },
  { value: '0 */6 * * *', label: 'Раз в 6 часов' },
  { value: '0 0 * * *', label: 'Раз в день' },
  { value: '0 0 * * 0', label: 'Раз в неделю' },
  { value: '0 0 1 * *', label: 'Раз в месяц' },
  { value: '0 0 1 */3 *', label: 'Раз в 3 месяца' },
  { value: '0 0 1 */6 *', label: 'Раз в 6 месяцев' },
];
