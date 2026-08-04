import React, { useMemo, useState } from 'react';
import { Form, Modal, Space, InputNumber, Button } from 'antd';
import { useModalStore, useNotifications } from '@portfolio/shared';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import AssetSelect from 'src/features/forms/AssetSelect';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import DateSubview from 'src/features/forms/DateSubview';
import CommentSubview from 'src/features/forms/CommentSubview';
import { useOverviewData } from 'src/modules/portfolios/hooks/useOverviewData';
import { useTransactionOperations } from 'src/modules/transaction/hooks/useTransactionOperations';
import { useSubview } from 'src/hooks/useSubview';
import dayjs from 'dayjs';

const WalletFundingModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { walletId, portfolioId } = modalProps;
  const { allWallets, getPortfolio } = useOverviewData();
  const { editTransaction, loading } = useTransactionOperations();

  const [form] = Form.useForm();
  const [selectedTicker, setSelectedTicker] = useState(null);
  const { subview, openSubview, closeSubview } = useSubview();

  const wallet = useMemo(() => (allWallets || []).find(w => w.id === walletId), [allWallets, walletId]);
  const portfolio = getPortfolio(portfolioId);
  const markets = !portfolio?.market
    ? null
    : portfolio.market === 'currency'
      ? ['currency']
      : [portfolio.market, 'currency'];

  const date = Form.useWatch('date', { form, preserve: true });

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      walletId,
      portfolioId,
      date: values.date.toISOString?.() || new Date(values.date).toISOString(),
      type: 'Input',
    };
    const result = await editTransaction(null, submitData);

    if (result.success) {
      success('Кошелёк пополнен');
      closeModal();
    } else {
      error(result.error || 'Произошла ошибка при пополнении кошелька');
    }
  };

  const handleCancel = () => {
    form.resetFields();
    closeModal();
  };

  return (
    <Modal
      title={subview ? null : "Пополнить кошелёк"}
      open={true}
      onCancel={handleCancel}
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
        initialValues={{
          date: dayjs(),
        }}
      >
        {subview === 'date' ? (
          <DateSubview onClose={closeSubview} />
        ) : subview === 'comment' ? (
          <CommentSubview onClose={closeSubview} />
        ) : (
          <>
            <div style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: 24 }}>
              Кошелёк: {wallet?.name || '—'} · Портфель: {portfolio?.name || '—'}
            </div>

            <AssetSelect
              name="tickerId"
              rules={[{ required: true, message: 'Выберите актив' }]}
              markets={markets}
              onTickerChange={setSelectedTicker}
            />

            <Form.Item
              label="Количество"
              name="quantity"
              rules={[{ required: true, message: 'Введите количество' }]}
            >
              <Space.Compact style={{ width: '100%' }}>
                <Button style={{ pointerEvents: 'none' }}>{selectedTicker?.symbol || '—'}</Button>
                <InputNumber
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  style={{ width: '100%' }}
                />
              </Space.Compact>
            </Form.Item>

            <MetaRowGroup
              date={date}
              onDate={() => openSubview('date')}
              onComment={() => openSubview('comment')}
            />

            <FormActionBtns
              title="Пополнить"
              onCancel={handleCancel}
              loading={loading}
            />
          </>
        )}
      </Form>
    </Modal>
  );
};

export default WalletFundingModal;
