/**
 * Emissions Screen
 * Carbon tracking and emissions data
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

const EmissionsScreen = () => {
  const user = useSelector((state: RootState) => state.auth.user);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    if (!user?.organization_id) return;

    try {
      const response = await api.getEmissionsSummary(user.organization_id);
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to fetch emissions summary:', error);
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
        <Text style={styles.title}>Carbon Tracking</Text>
        <Text style={styles.subtitle}>Emissions by scope</Text>

        {summary && (
          <>
            <View style={styles.totalCard}>
              <Text style={styles.totalLabel}>Total Emissions</Text>
              <Text style={styles.totalValue}>
                {summary.total_emissions_kg?.toFixed(1)} kg CO₂
              </Text>
            </View>

            <View style={styles.card}>
              <ScopeRow
                scope="Scope 1"
                description="Direct emissions"
                value={summary.scope1_kg}
                color={COLORS.error}
              />
              <ScopeRow
                scope="Scope 2"
                description="Energy indirect"
                value={summary.scope2_kg}
                color={COLORS.warning}
              />
              <ScopeRow
                scope="Scope 3"
                description="Value chain"
                value={summary.scope3_kg}
                color={COLORS.success}
              />
            </View>
          </>
        )}
      </View>
    </ScrollView>
  );
};

interface ScopeRowProps {
  scope: string;
  description: string;
  value: number;
  color: string;
}

const ScopeRow: React.FC<ScopeRowProps> = ({ scope, description, value, color }) => (
  <View style={styles.scopeRow}>
    <View style={styles.scopeInfo}>
      <Text style={styles.scopeLabel}>{scope}</Text>
      <Text style={styles.scopeDescription}>{description}</Text>
    </View>
    <Text style={[styles.scopeValue, { color }]}>
      {value?.toFixed(1)} kg
    </Text>
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
  totalCard: {
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
    alignItems: 'center',
  },
  totalLabel: {
    fontSize: FONTS.sizes.base,
    color: COLORS.white,
    marginBottom: SPACING.xs,
  },
  totalValue: {
    fontSize: FONTS.sizes['3xl'],
    fontWeight: 'bold',
    color: COLORS.white,
  },
  card: {
    backgroundColor: COLORS.dark.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
  },
  scopeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.dark.border,
  },
  scopeInfo: {
    flex: 1,
  },
  scopeLabel: {
    fontSize: FONTS.sizes.base,
    fontWeight: '600',
    color: COLORS.white,
    marginBottom: SPACING.xs,
  },
  scopeDescription: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
  },
  scopeValue: {
    fontSize: FONTS.sizes.lg,
    fontWeight: 'bold',
  },
});

export default EmissionsScreen;
