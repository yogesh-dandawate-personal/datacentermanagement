/**
 * Dashboard Screen
 * Overview of facility metrics
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../redux/store';
import { api } from '../services/api';
import { COLORS, SPACING, FONTS, BORDER_RADIUS, SHADOWS } from '../utils/constants';

interface DashboardData {
  current_power_kw: number;
  daily_energy_kwh: number;
  pue: number;
  temperature_c: number;
  daily_emissions_kg: number;
  active_alarms: number;
}

const DashboardScreen = () => {
  const user = useSelector((state: RootState) => state.auth.user);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    if (!user?.organization_id) return;

    try {
      const response = await api.getDashboardSummary(user.organization_id);
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.content}>
        <Text style={styles.greeting}>Welcome, {user?.name}</Text>

        <View style={styles.grid}>
          <MetricCard
            title="Current Power"
            value={data?.current_power_kw?.toFixed(1) || '0'}
            unit="kW"
            color={COLORS.primary}
          />
          <MetricCard
            title="Daily Energy"
            value={data?.daily_energy_kwh?.toFixed(1) || '0'}
            unit="kWh"
            color={COLORS.secondary}
          />
          <MetricCard
            title="PUE"
            value={data?.pue?.toFixed(2) || '0'}
            unit=""
            color={COLORS.info}
          />
          <MetricCard
            title="Temperature"
            value={data?.temperature_c?.toFixed(1) || '0'}
            unit="°C"
            color={COLORS.warning}
          />
          <MetricCard
            title="Daily Emissions"
            value={data?.daily_emissions_kg?.toFixed(1) || '0'}
            unit="kg CO₂"
            color={COLORS.success}
          />
          <MetricCard
            title="Active Alarms"
            value={data?.active_alarms?.toString() || '0'}
            unit=""
            color={COLORS.error}
          />
        </View>
      </View>
    </ScrollView>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  unit: string;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, color }) => (
  <View style={[styles.card, SHADOWS.md]}>
    <Text style={styles.cardTitle}>{title}</Text>
    <View style={styles.cardValue}>
      <Text style={[styles.value, { color }]}>{value}</Text>
      <Text style={styles.unit}>{unit}</Text>
    </View>
  </View>
);

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
  content: {
    padding: SPACING.md,
  },
  greeting: {
    fontSize: FONTS.sizes.xl,
    fontWeight: 'bold',
    color: COLORS.white,
    marginBottom: SPACING.lg,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  card: {
    backgroundColor: COLORS.dark.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    marginBottom: SPACING.md,
    width: '48%',
  },
  cardTitle: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
    marginBottom: SPACING.sm,
  },
  cardValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  value: {
    fontSize: FONTS.sizes['2xl'],
    fontWeight: 'bold',
  },
  unit: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
    marginLeft: SPACING.xs,
  },
});

export default DashboardScreen;
