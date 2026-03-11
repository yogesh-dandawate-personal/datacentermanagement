/**
 * Navigation Configuration
 *
 * Structure:
 * - Stack Navigator (root)
 *   - Auth Screen (login/signup)
 *   - Main Tab Navigator
 *     - Dashboard
 *     - Energy
 *     - Emissions
 *     - Alarms
 *     - Settings
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useSelector } from 'react-redux';

import AuthScreen from './screens/AuthScreen';
import DashboardScreen from './screens/DashboardScreen';
import EnergyScreen from './screens/EnergyScreen';
import EmissionsScreen from './screens/EmissionsScreen';
import AlarmsScreen from './screens/AlarmsScreen';
import SettingsScreen from './screens/SettingsScreen';

import { RootState } from './redux/store';
import { COLORS } from './utils/constants';

// Type definitions
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type MainTabParamList = {
  Dashboard: undefined;
  Energy: undefined;
  Emissions: undefined;
  Alarms: undefined;
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

/**
 * Main Tab Navigator
 */
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
              break;
            case 'Energy':
              iconName = focused ? 'lightning-bolt' : 'lightning-bolt-outline';
              break;
            case 'Emissions':
              iconName = focused ? 'cloud' : 'cloud-outline';
              break;
            case 'Alarms':
              iconName = focused ? 'bell' : 'bell-outline';
              break;
            case 'Settings':
              iconName = focused ? 'cog' : 'cog-outline';
              break;
            default:
              iconName = 'help-circle-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.gray,
        headerShown: true,
        headerStyle: {
          backgroundColor: COLORS.dark.card,
        },
        headerTintColor: COLORS.white,
        tabBarStyle: {
          backgroundColor: COLORS.dark.card,
          borderTopColor: COLORS.dark.border,
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen
        name="Energy"
        component={EnergyScreen}
        options={{ title: 'Energy Metrics' }}
      />
      <Tab.Screen
        name="Emissions"
        component={EmissionsScreen}
        options={{ title: 'Carbon Tracking' }}
      />
      <Tab.Screen
        name="Alarms"
        component={AlarmsScreen}
        options={{ title: 'Alerts' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

/**
 * Root Stack Navigator
 */
function Navigation() {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {!isAuthenticated ? (
        <Stack.Screen name="Auth" component={AuthScreen} />
      ) : (
        <Stack.Screen name="Main" component={MainTabs} />
      )}
    </Stack.Navigator>
  );
}

export default Navigation;
