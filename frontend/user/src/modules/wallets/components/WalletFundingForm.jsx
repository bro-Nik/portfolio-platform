import React, { useMemo, useState } from 'react';
import { Form, Segmented } from 'antd';
import { useNotifications } from '@portfolio/shared';
import FormActionBtns from 'src/features/forms/FormActionBtns';
import AssetSelect from 'src/features/forms/AssetSelect';
import FormQuantityInput from 'src/features/forms/FormQuantityInput';
import MetaRowGroup from 'src/components/ui/MetaRowGroup';
import DateSubview from 'src/features/forms/DateSubview';
import CommentSubview from 'src/features/forms/CommentSubview';
import { useOverviewData } from 'src/modules/portfolios/hooks/useOverviewData';
import { useTransactionOperations } from 'src/modules/transaction/hooks/useTransactionOperations';
import { useSubview } from 'src/hooks/useSubview';
import dayjs from 'dayjs';

const WalletFundingForm = ({ walletId, portfolioId, onSuccess, onCancel }) => {
  const { success, error } = useNotifications();
  const { allWallets, getPortfolio } = useOverviewData();
  const { editTransaction, loading } = useTransactionOperations();

  const [form] = Form.useForm();
  const [selectedTicker, setSelectedTicker] = useState(null);
  const { subview, openSubview, closeSubview } = useSubview();

  const wallet = useMemo(() => (allWallets || []).find(w => w.id === walletId), [allWallets, walletId]);
  const portfolio = getPortfolio(portfolioId);

  const marketLabels = { crypto: 'Крипто', stocks: 'Акции', currency: 'Валюта' };

  const allowedMarkets = portfolio?.market === 'currency'
    ? ['currency']
    : portfolio?.market
      ? [portfolio.market, 'currency']
      : ['crypto', 'stocks', 'currency'];

  const marketOptions = allowedMarkets.map(m => ({ value: m, label: marketLabels[m] }));
  const [marketFilter, setMarketFilter] = useState(null);
  const effectiveMarket = marketFilter || allowedMarkets[0];
  const markets = effectiveMarket === 'currency' ? ['currency'] : [effectiveMarket, 'currency'];

  const date = Form.useWatch('date', { form, preserve: true });

  const handleSubmit = async (values) => {
    const dateValue = form.getFieldValue('date');
    const submitData = {
      ...values,
      walletId,
      portfolioId,
      date: dateValue?.toISOString?.() || (dateValue ? new Date(dateValue).toISOString() : new Date().toISOString()),
      type: 'Input',
    };
    const result = await editTransaction(null, submitData);

    if (result.success) {
      success('Кошелёк пополнен');
      onSuccess?.(result.data);
    } else {
      error(result.error || 'Произошла ошибка при пополнении кошелька');
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onCancel?.();
  };

  return (
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

          <Form.Item>
            <Segmented value={effectiveMarket} onChange={setMarketFilter} options={marketOptions} />
          </Form.Item>

          <AssetSelect
            name="tickerId"
            rules={[{ required: true, message: 'Выберите актив' }]}
            markets={markets}
            onTickerChange={setSelectedTicker}
            variant="filled"
          />

          <FormQuantityInput showFree={false} ticker={selectedTicker?.symbol} />

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
  );
};

export default WalletFundingForm;
