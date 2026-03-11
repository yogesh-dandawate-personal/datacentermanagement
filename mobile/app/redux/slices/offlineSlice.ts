/**
 * Offline Redux Slice
 *
 * Handles offline queue and sync status
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface QueuedAction {
  id: string;
  type: string;
  payload: any;
  timestamp: string;
  retries: number;
}

interface OfflineState {
  isOnline: boolean;
  queue: QueuedAction[];
  syncing: boolean;
  lastSync: string | null;
  errors: string[];
}

const initialState: OfflineState = {
  isOnline: true,
  queue: [],
  syncing: false,
  lastSync: null,
  errors: [],
};

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    addToQueue: (state, action: PayloadAction<QueuedAction>) => {
      state.queue.push(action.payload);
    },
    removeFromQueue: (state, action: PayloadAction<string>) => {
      state.queue = state.queue.filter((item) => item.id !== action.payload);
    },
    incrementRetries: (state, action: PayloadAction<string>) => {
      const item = state.queue.find((q) => q.id === action.payload);
      if (item) {
        item.retries += 1;
      }
    },
    startSync: (state) => {
      state.syncing = true;
      state.errors = [];
    },
    syncSuccess: (state) => {
      state.syncing = false;
      state.lastSync = new Date().toISOString();
      state.queue = [];
    },
    syncFailure: (state, action: PayloadAction<string>) => {
      state.syncing = false;
      state.errors.push(action.payload);
    },
    clearQueue: (state) => {
      state.queue = [];
      state.errors = [];
    },
  },
});

export const {
  setOnlineStatus,
  addToQueue,
  removeFromQueue,
  incrementRetries,
  startSync,
  syncSuccess,
  syncFailure,
  clearQueue,
} = offlineSlice.actions;

export default offlineSlice.reducer;
