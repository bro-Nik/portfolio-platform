import { getWatchlist } from 'src/api';

const watchlist = getWatchlist();

export const watchlistApi = {
  getWatchlist: () => watchlist.getWatchlistApiWatchlistGet(),

  addItem: (tickerId, comment) => watchlist.addWatchlistItemApiWatchlistPost({ tickerId, comment }),

  updateItem: (itemId, comment) => watchlist.updateWatchlistItemApiWatchlistItemIdPut(itemId, { comment }),

  deleteItem: (itemId) => watchlist.deleteWatchlistItemApiWatchlistItemIdDelete(itemId),

  archiveItem: (itemId, isArchived) =>
    watchlist.setWatchlistItemArchivedApiWatchlistItemIdPatch(itemId, { isArchived }),

  getItemAlerts: (itemId) => watchlist.getItemAlertsApiWatchlistItemIdAlertsGet(itemId),

  createAlert: (itemId, data) => watchlist.createAlertApiWatchlistItemIdAlertsPost(itemId, data),

  updateAlert: (alertId, data) => watchlist.updateAlertApiWatchlistAlertsAlertIdPut(alertId, data),

  deleteAlert: (alertId) => watchlist.deleteAlertApiWatchlistAlertsAlertIdDelete(alertId),

  archiveAlert: (alertId, isArchived) =>
    watchlist.setAlertArchivedApiWatchlistAlertsAlertIdPatch(alertId, { isArchived }),

  getTriggered: () => watchlist.getTriggeredAlertsApiWatchlistAlertsTriggeredGet(),
};
