import React, { useMemo, useState } from 'react';
import { Form, Modal, Space, InputNumber, Button } from 'antd';
import { useModalStore, useNotifications } from '@portfolio/shared';
import FormDate from 'src/features/forms/FormDate';
import FormComment from 'src/features/forms/FormComment';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import ShowMore from 'src/components/ui/ShowMore';
import AssetSelect from 'src/features/forms/AssetSelect';
import { useOverviewData } from 'src/modules/portfolios/hooks/useOverviewData';
import { useTransactionOperations } from 'src/modules/transaction/hooks/useTransactionOperations';
import { toDatetimeLocal } from 'src/utils/format';

const WalletFundingModal = () => {
  const { success, error } = useNotifications();
  const { modalProps, closeModal } = useModalStore();
  const { walletId, portfolioId } = modalProps;
  const { allWallets, getPortfolio } = useOverviewData();
  const { editTransaction, loading } = useTransactionOperations();

  const [form] = Form.useForm();
  const [selectedTicker, setSelectedTicker] = useState(null);

  const wallet = useMemo(() => (allWallets || []).find(w => w.id === walletId), [allWallets, walletId]);
  const portfolio = getPortfolio(portfolioId);
  const markets = !portfolio?.market
    ? null
    : portfolio.market === 'currency'
      ? ['currency']
      : [portfolio.market, 'currency'];

  const handleSubmit = async (values) => {
    const submitData = {
      ...values,
      walletId,
      portfolioId,
      date: new Date(values.date).toISOString(),
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
      title="Пополнить кошелёк"
      open={true}
      onCancel={handleCancel}
      footer={null}
      width={500}
      destroyOnHidden
    >
      <Form
        form={form}
        onFinish={handleSubmit}
        requiredMark={false}
        size="middle"
        initialValues={{
          date: toDatetimeLocal(new Date()),
        }}
      >
        <Space orientation="vertical" style={{ width: '100%' }} size="middle">
          <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
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

          <FormDate />

          <ShowMore content={<FormComment />} />

          <FormActionBtns
            title="Пополнить"
            onCancel={handleCancel}
            loading={loading}
          />
        </Space>
      </Form>
    </Modal>
  );
};

export default WalletFundingModal;
