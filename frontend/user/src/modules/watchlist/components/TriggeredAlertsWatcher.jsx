import { useEffect, useRef } from 'react';
import { useNotifications } from '@portfolio/shared';
import { useTriggeredAlerts } from 'src/modules/watchlist/hooks/useTriggeredAlerts';

/** Тосты о новых сработавших уведомлениях. Монтируется один раз в сайдбаре. */
const TriggeredAlertsWatcher = () => {
  const { info } = useNotifications();
  const { data: alerts = [] } = useTriggeredAlerts();
  const prevIds = useRef(null);

  useEffect(() => {
    const ids = new Set(alerts.map(a => a.id));
    if (prevIds.current === null) {
      prevIds.current = ids;
      return;
    }
    const fresh = alerts.filter(a => !prevIds.current.has(a.id));
    prevIds.current = ids;
    fresh.forEach(a => {
      const symbol = a.tickerSymbol?.toUpperCase() || 'Актив';
      info(`«${symbol}»: цена ${a.direction === 'above' ? 'выше' : 'ниже'} целевой — уведомление сработало`);
    });
  }, [alerts, info]);

  return null;
};

export default TriggeredAlertsWatcher;
