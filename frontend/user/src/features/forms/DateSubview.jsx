import { Button, Calendar, Form, Select, TimePicker } from 'antd';
import ruRU from 'antd/es/locale/ru_RU';
import SubviewHeader from 'src/components/ui/SubviewHeader';

const YEAR_SELECT_OFFSET = 10;
const YEAR_SELECT_TOTAL = 20;

const DateSubview = ({ onClose }) => {
  const form = Form.useFormInstance();
  const date = Form.useWatch('date', { form, preserve: true });

  const handleCalendarChange = (value) => {
    form.setFieldValue('date', value);
  };

  const handleTimeChange = (value) => {
    if (!date) return;
    form.setFieldValue('date', date.hour(value.hour()).minute(value.minute()));
  };

  const headerRender = ({ value, onChange }) => {
    const year = value.year();
    const start = year - YEAR_SELECT_OFFSET;
    const months = ruRU.Calendar.lang.shortMonths;

    const yearOptions = Array.from({ length: YEAR_SELECT_TOTAL }, (_, i) => ({
      label: String(start + i),
      value: start + i,
    }));

    const monthOptions = months.map((label, i) => ({ label, value: i }));

    return (
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <Select
          style={{ flex: 1 }}
          options={monthOptions}
          value={value.month()}
          variant="filled"
          onChange={(month) => onChange(value.month(month))}
        />
        <Select
          style={{ flex: 1 }}
          options={yearOptions}
          value={year}
          variant="filled"
          onChange={(numYear) => onChange(value.year(numYear))}
        />
      </div>
    );
  };

  return (
    <>
      <SubviewHeader title="Дата и время" onBack={onClose} />

      <Form.Item
        name="date"
        rules={[{ required: true, message: 'Выберите дату' }]}
      >
        <Calendar
          fullscreen={false}
          value={date}
          onChange={handleCalendarChange}
          headerRender={headerRender}
        />
      </Form.Item>

      <Form.Item label="Время">
        <TimePicker
          format="HH:mm"
          style={{ width: '100%' }}
          value={date}
          onChange={handleTimeChange}
          placeholder="Время"
          variant="filled"
        />
      </Form.Item>

      <Button type="primary" onClick={onClose} block>
        Добавить
      </Button>
    </>
  );
};

export default DateSubview;
