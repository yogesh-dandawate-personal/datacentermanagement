/**
 * Settings Screen
 * User profile and app preferences
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../redux/slices/authSlice';
import { RootState } from '../redux/store';
import { COLORS, SPACING, FONTS, BORDER_RADIUS } from '../utils/constants';

const SettingsScreen = () => {
  const dispatch = useDispatch();
  const user = useSelector((state: RootState) => state.auth.user);
  const [notificationsEnabled, setNotificationsEnabled] = React.useState(true);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* User Profile */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Profile</Text>
          <View style={styles.card}>
            <View style={styles.profileRow}>
              <Icon name="account" size={24} color={COLORS.primary} />
              <View style={styles.profileInfo}>
                <Text style={styles.profileLabel}>Name</Text>
                <Text style={styles.profileValue}>{user?.name}</Text>
              </View>
            </View>
            <View style={styles.profileRow}>
              <Icon name="email" size={24} color={COLORS.primary} />
              <View style={styles.profileInfo}>
                <Text style={styles.profileLabel}>Email</Text>
                <Text style={styles.profileValue}>{user?.email}</Text>
              </View>
            </View>
            <View style={styles.profileRow}>
              <Icon name="office-building" size={24} color={COLORS.primary} />
              <View style={styles.profileInfo}>
                <Text style={styles.profileLabel}>Organization</Text>
                <Text style={styles.profileValue}>{user?.organization_id}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* App Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Settings</Text>
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Icon name="bell" size={24} color={COLORS.primary} />
                <Text style={styles.settingLabel}>Push Notifications</Text>
              </View>
              <Switch
                value={notificationsEnabled}
                onValueChange={setNotificationsEnabled}
                trackColor={{ false: COLORS.gray, true: COLORS.primary }}
              />
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Icon name="logout" size={24} color={COLORS.white} />
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>

        {/* App Info */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>iNetZero Mobile v1.0.0</Text>
          <Text style={styles.footerText}>© 2026 iNetZero</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.dark.background,
  },
  content: {
    padding: SPACING.md,
  },
  section: {
    marginBottom: SPACING.lg,
  },
  sectionTitle: {
    fontSize: FONTS.sizes.lg,
    fontWeight: 'bold',
    color: COLORS.white,
    marginBottom: SPACING.md,
  },
  card: {
    backgroundColor: COLORS.dark.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
  },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.dark.border,
  },
  profileInfo: {
    marginLeft: SPACING.md,
  },
  profileLabel: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
  },
  profileValue: {
    fontSize: FONTS.sizes.base,
    color: COLORS.white,
    marginTop: SPACING.xs,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.md,
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingLabel: {
    fontSize: FONTS.sizes.base,
    color: COLORS.white,
    marginLeft: SPACING.md,
  },
  logoutButton: {
    backgroundColor: COLORS.error,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoutText: {
    color: COLORS.white,
    fontSize: FONTS.sizes.lg,
    fontWeight: '600',
    marginLeft: SPACING.sm,
  },
  footer: {
    alignItems: 'center',
    marginTop: SPACING.xl,
  },
  footerText: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.gray,
    marginBottom: SPACING.xs,
  },
});

export default SettingsScreen;
