import { beforeEach, describe, expect, it } from 'vitest';
import useNavigationStore from './navigationStore';

const item = { id: 7, name: 'Bitcoin', symbol: 'BTC', tickerId: 62709 };

beforeEach(() => {
  useNavigationStore.getState().actions.resetNavigation();
});

describe('wishlist tabs', () => {
  it('opens a watchlist item in the wishlist section', () => {
    const { openItem, getItem } = useNavigationStore.getState().actions;

    openItem(item, 'wishlist_item');

    const state = useNavigationStore.getState();
    expect(state.activeSection).toBe('wishlist_item-7');
    expect(getItem('wishlist', 7, 'wishlist_item')).toMatchObject({ id: 7, name: 'Bitcoin' });
  });

  it('reopening toggles back to the section', () => {
    const { openItem, setActiveSection } = useNavigationStore.getState().actions;

    setActiveSection('wishlist');
    openItem(item, 'wishlist_item');
    openItem(item, 'wishlist_item');

    expect(useNavigationStore.getState().activeSection).toBe('wishlist');
  });

  it('closing the active item falls back to wishlist', () => {
    const { openItem, closeItem, setActiveSection } = useNavigationStore.getState().actions;

    setActiveSection('wishlist');
    openItem(item, 'wishlist_item');
    closeItem(7, 'wishlist_item');

    const state = useNavigationStore.getState();
    expect(state.activeSection).toBe('wishlist');
    expect(state.openedItems.wishlist).toHaveLength(0);
  });
});
