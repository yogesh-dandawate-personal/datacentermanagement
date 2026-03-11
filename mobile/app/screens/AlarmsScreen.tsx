/**
 * Alarms Screen
 * List of active alarms and alerts
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';
import { RootState } from '../redux/store';
import { api } from '../services/api';
import { COLORS, SPACING, FONTS, BORDER_RADIUS } from '../utils/constants';

interface Alarm {
  id: string;
  type: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

const AlarmsScreen = () => {
  const user = useSelector((state: RootState) => state.auth.user);
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAlarms = async () => {
    if (!user?.organization_id) return;

    try {
      const response = await api.getAlarms(user.organization_id);
      setAlarms(response.data);
    } catch (error) {
      console.error('Failed to fetch alarms:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAlarms();
  }, []);

  const handleAcknowledge = async (alarmId: string) => {
    try {
      await api.acknowledgeAlarm(alarmId);
      setAlarms((prev) =>
        prev.map((alarm) =>
          alarm.id === alarmId ? { ...alarm, acknowledged: true } : alarm
        )
      );
    } catch (error) {
      console.error('Failed to acknowledge alarm:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchAlarms();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return COLORS.error;
      case 'warning':
        return COLORS.warning;
      default:
        return COLORS.info;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'alert-circle';
      case 'warning':
        return 'alert';
      default:
        return 'information';
    }
  };

  const renderAlarm = ({ item }: { item: Alarm }) => (
    <View style={styles.alarmCard}>
      <View style={styles.alarmHeader}>
        <Icon
          name={getSeverityIcon(item.severity)}
          size={24}
          color={getSeverityColor(item.severity)}
        />
        <View style={styles.alarmInfo}>
          <Text style={styles.alarmType}>{item.type}</Text>
          <Text style={styles.alarmTime}>
            {new Date(item.timestamp).toLocaleString()}
          </Text>
        </View>
      </View>
      <Text style={styles.alarmMessage}>{item.message}</Text>
      {!item.acknowledged && (
        <TouchableOpacity
          style={styles.ackButton}
          onPress={() => handleAcknowledge(item.id)}
        >
          <Text style={styles.ackButtonText}>Acknowledge</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={alarms}
        keyExtractor={(item) => item.id}
        renderItem={renderAlarm}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="check-circle" size={64} color={COLORS.success} />
            <Text style={styles.emptyText}>No active alarms</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.dark.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.dark.background,
  },
  list: {
    padding: SPACING.md,
  },
  alarmCard: {
    backgroundColor: COLORS.dark.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    marginBottom: SPACING.md,
  },
  alarmHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  alarmInfo: {
    marginLeft: SPACING.md,
    flex: 1,
  },
  alarmType: {
    fontSize: FONTS.sizes.base,
    fontWeight: '600',
    color: COLORS.white,
  },
  alarmTime: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
  },
  alarmMessage: {
    fontSize: FONTS.sizes.base,
    color: COLORS.white,
    marginBottom: SPACING.md,
  },
  ackButton: {
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.sm,
    alignItems: 'center',
  },
  ackButtonText: {
    color: COLORS.white,
    fontSize: FONTS.sizes.sm,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING['2xl'],
  },
  emptyText: {
    fontSize: FONTS.sizes.lg,
    color: COLORS.gray,
    marginTop: SPACING.md,
  },
});

export default AlarmsScreen;
