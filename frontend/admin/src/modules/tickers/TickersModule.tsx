import React, { useState } from 'react';
import { Button, Input, Select, Space, Typography, Row, Col, Card, Statistic } from 'antd';
import { MergeCellsOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { TickerTable } from './components/TickerTable';
import { useTickers } from './hooks/useTickers';
import { useTickerModals } from './hooks/useTickerModals';
import { useDebounce } from '../../hooks/useDebounce';
import { QueryError } from '../../components/QueryError';

export const TickersModule: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [market, setMarket] = useState<string | undefined>(undefined);
  const pageSize = 20;

  const debouncedSearch = useDebounce(search, 300);
  const { data, isLoading, error } = useTickers({ search: debouncedSearch, market, page, pageSize });
  const { editModal, mergeModal } = useTickerModals();

  if (error) return <QueryError title='Ошибка загрузки тикеров' error={error} />;

  const stats = {
    total: data?.total ?? 0,
  };

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic title="Всего тикеров" value={stats.total} />
          </Card>
        </Col>
      </Row>

      <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }} align="center">
        <Space>
          <Input
            placeholder="Поиск по названию или символу"
            prefix={<SearchOutlined />}
            allowClear
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            style={{ width: 300 }}
          />
          <Select
            placeholder="Все рынки"
            allowClear
            value={market}
            onChange={v => { setMarket(v); setPage(1); }}
            style={{ width: 150 }}
            options={[
              { value: 'crypto', label: 'Криптовалюты' },
              { value: 'stocks', label: 'Акции' },
              { value: 'currency', label: 'Валюты' },
            ]}
          />
        </Space>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => setPage(1)}>Обновить</Button>
          <Button icon={<MergeCellsOutlined />} onClick={() => mergeModal()}>Слияние</Button>
        </Space>
      </Space>

      <TickerTable
        data={data?.data ?? []}
        loading={isLoading}
        page={page}
        pageSize={pageSize}
        total={stats.total}
        onPageChange={setPage}
      />
    </div>
  );
};
