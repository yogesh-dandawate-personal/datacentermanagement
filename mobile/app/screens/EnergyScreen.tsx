/**
 * Energy Screen
 * Energy metrics and trends
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
import { COLORS, SPACING, FONTS, BORDER_RADIUS } from '../utils/constants';

const EnergyScreen = () => {
  const user = useSelector((state: RootState) => state.auth.user);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    if (!user?.organization_id) return;

    try {
      const response = await api.getEnergyTrends(user.organization_id);
      setTrends(response.data);
    } catch (error) {
      console.error('Failed to fetch energy trends:', error);
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
        <Text style={styles.title}>Energy Metrics</Text>
        <Text style={styles.subtitle}>Real-time facility energy usage</Text>

        {trends && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>24-Hour Trend</Text>
            <View style={styles.row}>
              <View style={styles.stat}>
                <Text style={styles.label}>Average Power</Text>
                <Text style={styles.value}>
                  {trends.avg_power_kw?.toFixed(1)} kW
                </Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.label}>Peak Power</Text>
                <Text style={styles.value}>
                  {trends.peak_power_kw?.toFixed(1)} kW
                </Text>
              </View>
            </View>
            <View style={styles.row}>
              <View style={styles.stat}>
                <Text style={styles.label}>Total Energy</Text>
                <Text style={styles.value}>
                  {trends.total_energy_kwh?.toFixed(1)} kWh
                </Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.label}>Current PUE</Text>
                <Text style={styles.value}>
                  {trends.current_pue?.toFixed(2)}
                </Text>
              </View>
            </View>
          </View>
        )}
      </View>
    </ScrollView>
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
  content: {
    padding: SPACING.md,
  },
  title: {
    fontSize: FONTS.sizes['2xl'],
    fontWeight: 'bold',
    color: COLORS.white,
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: FONTS.sizes.base,
    color: COLORS.gray,
    marginBottom: SPACING.lg,
  },
  card: {
    backgroundColor: COLORS.dark.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    marginBottom: SPACING.md,
  },
  cardTitle: {
    fontSize: FONTS.sizes.lg,
    fontWeight: '600',
    color: COLORS.white,
    marginBottom: SPACING.md,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: SPACING.md,
  },
  stat: {
    flex: 1,
  },
  label: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
    marginBottom: SPACING.xs,
  },
  value: {
    fontSize: FONTS.sizes.xl,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
});

export default EnergyScreen;
