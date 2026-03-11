/**
 * Offline Sync Service
 *
 * Handles:
 * - Queue processing
 * - Conflict resolution
 * - Background sync
 */

import NetInfo from '@react-native-community/netinfo';
import { store } from '../redux/store';
import {
  setOnlineStatus,
  startSync,
  syncSuccess,
  syncFailure,
  removeFromQueue,
  incrementRetries,
} from '../redux/slices/offlineSlice';
import { api } from './api';
import {
  getSyncQueue,
  removeFromSyncQueue,
  incrementSyncRetries,
  saveEnergyMetrics,
  saveEmissions,
  saveAlarms,
} from './database';
import { SYNC_CONFIG } from '../utils/constants';

/**
 * Initialize sync monitoring
 */
export const initSync = (): void => {
  // Monitor network connectivity
  NetInfo.addEventListener(state => {
    const isOnline = state.isConnected ?? false;
    store.dispatch(setOnlineStatus(isOnline));

    if (isOnline) {
      syncOfflineQueue();
    }
  });

  // Periodic sync every 5 minutes
  setInterval(() => {
    const state = store.getState();
    if (state.offline.isOnline && state.offline.queue.length > 0) {
      syncOfflineQueue();
    }
  }, SYNC_CONFIG.INTERVAL);
};

/**
 * Sync offline queue
 */
export const syncOfflineQueue = async (): Promise<void> => {
  const state = store.getState();

  // Check if online and not already syncing
  if (!state.offline.isOnline || state.offline.syncing) {
    return;
  }

  store.dispatch(startSync());

  try {
    const queueItems = await getSyncQueue();

    console.log(`Processing ${queueItems.length} queued items`);

    for (const item of queueItems) {
      try {
        await processSyncItem(item);
        await removeFromSyncQueue(item.id);
        store.dispatch(removeFromQueue(item.id));
      } catch (error: any) {
        console.error(`Failed to sync item ${item.id}:`, error);

        // Increment retries
        await incrementSyncRetries(item.id, error.message);
        store.dispatch(incrementRetries(item.id));

        // Remove if max retries reached
        if (item.retries >= SYNC_CONFIG.MAX_RETRIES) {
          await removeFromSyncQueue(item.id);
          store.dispatch(removeFromQueue(item.id));
          console.log(`Removed item ${item.id} after max retries`);
        }
      }
    }

    store.dispatch(syncSuccess());
    console.log('Sync completed successfully');
  } catch (error: any) {
    store.dispatch(syncFailure(error.message));
    console.error('Sync failed:', error);
  }
};

/**
 * Process a single sync item
 */
const processSyncItem = async (item: any): Promise<void> => {
  const { action_type, endpoint, method, payload } = item;

  const parsedPayload = payload ? JSON.parse(payload) : null;

  switch (action_type) {
    case 'API_REQUEST':
      await replayApiRequest(endpoint, method, parsedPayload);
      break;

    case 'ACKNOWLEDGE_ALARM':
      await api.acknowledgeAlarm(parsedPayload.alarmId);
      break;

    case 'UPDATE_PROFILE':
      await api.updateUserProfile(parsedPayload);
      break;

    default:
      console.warn(`Unknown action type: ${action_type}`);
  }
};

/**
 * Replay API request
 */
const replayApiRequest = async (
  endpoint: string,
  method: string,
  data: any
): Promise<void> => {
  const requestConfig: any = {
    method,
    url: endpoint,
  };

  if (data) {
    if (method === 'GET') {
      requestConfig.params = data;
    } else {
      requestConfig.data = data;
    }
  }

  await api(requestConfig);
};

/**
 * Fetch and cache data for offline use
 */
export const fetchAndCacheData = async (facilityId: string): Promise<void> => {
  try {
    const now = new Date();
    const startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 days ago

    // Fetch energy metrics
    const energyResponse = await api.getEnergyMetrics(
      facilityId,
      startDate.toISOString(),
      now.toISOString()
    );
    await saveEnergyMetrics(energyResponse.data);

    // Fetch emissions
    const emissionsResponse = await api.getEmissions(
      facilityId,
      startDate.toISOString(),
      now.toISOString()
    );
    await saveEmissions(emissionsResponse.data);

    // Fetch alarms
    const alarmsResponse = await api.getAlarms(facilityId);
    await saveAlarms(alarmsResponse.data);

    console.log('Data cached successfully for offline use');
  } catch (error) {
    console.error('Failed to cache data:', error);
  }
};

/**
 * Conflict resolution strategy: Last Write Wins
 */
export const resolveConflict = (local: any, remote: any): any => {
  const localTime = new Date(local.updated_at).getTime();
  const remoteTime = new Date(remote.updated_at).getTime();

  // Return the newer version
  return remoteTime > localTime ? remote : local;
};

/**
 * Get sync status
 */
export const getSyncStatus = (): {
  isOnline: boolean;
  syncing: boolean;
  queueLength: number;
  lastSync: string | null;
} => {
  const state = store.getState();

  return {
    isOnline: state.offline.isOnline,
    syncing: state.offline.syncing,
    queueLength: state.offline.queue.length,
    lastSync: state.offline.lastSync,
  };
};
