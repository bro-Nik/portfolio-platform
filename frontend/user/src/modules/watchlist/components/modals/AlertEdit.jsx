import React, { useEffect, useMemo } from 'react';
import { Form, InputNumber, Modal, Segmented, Select } from 'antd';
import { useModalStore, useNotifications } from '@portfolio/shared';
import { useWatchlistOperations } from '../../hooks/useWatchlistOperations';
import { useCurrencies } from 'src/modules/assets/hooks/useCurrencies';
import { useDisplayCurrency } from 'src/utils/currency';
import { getCurrencyRate } from 'src/stores/preferencesStore';
import { formatCurrency, formatCurrencyFromUsd } from 'src/utils/format';
import { useSubview } from 'src/hooks/useSubview';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import CommentSubview from 'src/features/forms/CommentSubview';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import { deriveDirection, DIRECTION_LABELS } from '../../utils/alerts';

const AlertEditModal = () => {
  useDisplayCurrency();
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { item, alert = null } = modalProps;
  const { saveAlert, loading } = useWatchlistOperations();
  const { data: currencies = [] } = useCurrencies();
  const { subview, openSubview, closeSubview } = useSubview();
  const [form] = Form.useForm();

  const currencyOptions = useMemo(() => {
    const symbols = new Set(['USD', ...(currencies || []).map(t => t.symbol).filter(Boolean)]);
    return [...symbols].map(symbol => ({ value: symbol, label: symbol }));
  }, [currencies]);

  const initialCurrency = alert?.currencySymbol || 'USD';
  const initialRate = getCurrencyRate(initialCurrency);
  const initialTarget = alert && initialRate > 0 ? Number(alert.targetPriceUsd) / initialRate : undefined;

  useEffect(() => {
    form.setFieldsValue({
      direction: alert?.direction || deriveDirection(Number(item?.price), Number(alert?.targetPriceUsd)),
      currencySymbol: initialCurrency,
      target: initialTarget,
      comment: alert?.comment || '',
    });
  }, [alert, item, form, initialCurrency, initialTarget]);

  const watched = Form.useWatch([], form) || {};
  const direction = watched.direction;
  const currencySymbol = watched.currencySymbol || initialCurrency;
  const target = watched.target;

  const preview = useMemo(() => {
    const amount = Number(target);
    if (!amount || amount <= 0) return null;
    const usd = amount * getCurrencyRate(currencySymbol);
    const current = Number(item?.price);
    const implied = direction || deriveDirection(current, usd);
    return { usd, implied };
  }, [target, currencySymbol, direction, item?.price]);

  const handleSubmit = async () => {
    const values = form.getFieldsValue();
    const usd = Number(values.target) * getCurrencyRate(values.currencySymbol);
    if (!usd || usd <= 0) {
      error('Введите корректную целевую цену');
      return;
    }
    const result = await saveAlert(item.id, alert, {
      direction: values.direction || deriveDirection(Number(item?.price), usd),
      targetPriceUsd: String(usd),
      currencySymbol: values.currencySymbol,
      comment: form.getFieldValue('comment') || null,
    });
    if (result.success) {
      success(alert ? 'Уведомление обновлено' : 'Уведомление создано');
      closeModal();
    } else {
      error(result.error || 'Произошла ошибка');
    }
  };

  const handleCancel = () => {
    form.resetFields();
    closeModal();
  };

  return (
    <Modal
      title={subview ? null : (alert ? 'Изменить уведомление' : 'Добавить уведомление')}
      open={true}
      onCancel={closeModal}
      closable={!subview}
      footer={null}
      width={500}
      destroyOnHidden
    >
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
        requiredMark={false}
        size="middle"
      >
        {subview === 'comment' ? (
          <CommentSubview onClose={closeSubview} />
        ) : (
          <>
            <Form.Item label="Условие" name="direction">
              <Segmented
                block
                options={[
                  { value: 'below', label: 'Упадёт ниже' },
                  { value: 'above', label: 'Вырастет выше' },
                ]}
              />
            </Form.Item>
            <div style={{ display: 'flex', gap: 8 }}>
              <Form.Item
                label="Целевая цена"
                name="target"
                rules={[{ required: true, message: 'Введите цену' }]}
                style={{ flex: 1 }}
              >
                <InputNumber autoFocus min={0} style={{ width: '100%' }} variant="filled" placeholder="0.00" />
              </Form.Item>
              <Form.Item label="Валюта" name="currencySymbol" style={{ width: 130 }}>
                <Select options={currencyOptions} variant="filled" showSearch optionFilterProp="label" />
              </Form.Item>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12 }}>
              Сейчас: {formatCurrencyFromUsd(item?.price)}
              {preview && (
                <>
                  {' '}→ порог {formatCurrency(preview.usd, 'USD', 'ru-RU', true)}
                  {preview.implied && ` (${DIRECTION_LABELS[preview.implied].toLowerCase()} текущей)`}
                </>
              )}
            </div>
            <MetaRowGroup onComment={() => openSubview('comment')} />
            <FormActionBtns title={alert ? 'Сохранить' : 'Создать'} onCancel={handleCancel} loading={loading} />
          </>
        )}
      </Form>
    </Modal>
  );
};

export default AlertEditModal;
