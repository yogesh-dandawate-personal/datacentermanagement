package com.inetzero;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

/**
 * Firebase Cloud Messaging Service
 *
 * Handles:
 * - Remote notifications from FCM
 * - Notification display
 * - Notification actions
 * - Token management
 */
public class NotificationService extends FirebaseMessagingService {

    private static final String TAG = "NotificationService";
    private static final String DEFAULT_CHANNEL_ID = "default";
    private static final String ALARM_CHANNEL_ID = "alarms";

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannels();
    }

    /**
     * Called when a new FCM token is generated
     */
    @Override
    public void onNewToken(String token) {
        super.onNewToken(token);
        android.util.Log.d(TAG, "New FCM token: " + token);

        // Send token to backend
        sendTokenToBackend(token);
    }

    /**
     * Called when a remote message is received
     */
    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);

        android.util.Log.d(TAG, "Message received from: " + remoteMessage.getFrom());

        // Check if message contains data payload
        if (remoteMessage.getData().size() > 0) {
            android.util.Log.d(TAG, "Message data: " + remoteMessage.getData());
            handleDataMessage(remoteMessage.getData());
        }

        // Check if message contains notification payload
        if (remoteMessage.getNotification() != null) {
            android.util.Log.d(TAG, "Message notification: " + remoteMessage.getNotification().getBody());
            showNotification(
                remoteMessage.getNotification().getTitle(),
                remoteMessage.getNotification().getBody(),
                remoteMessage.getData()
            );
        }
    }

    /**
     * Handle data message
     */
    private void handleDataMessage(Map<String, String> data) {
        String type = data.get("type");
        String title = data.get("title");
        String body = data.get("body");

        if (type != null && title != null && body != null) {
            String channelId = "critical".equals(data.get("severity")) ? ALARM_CHANNEL_ID : DEFAULT_CHANNEL_ID;
            showNotification(title, body, data, channelId);
        }
    }

    /**
     * Show notification
     */
    private void showNotification(String title, String body, Map<String, String> data) {
        showNotification(title, body, data, DEFAULT_CHANNEL_ID);
    }

    private void showNotification(String title, String body, Map<String, String> data, String channelId) {
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

        // Add data to intent
        for (Map.Entry<String, String> entry : data.entrySet()) {
            intent.putExtra(entry.getKey(), entry.getValue());
        }

        int flags = PendingIntent.FLAG_ONE_SHOT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }

        PendingIntent pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            flags
        );

        Uri defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, channelId)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(true)
            .setSound(defaultSoundUri)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(pendingIntent);

        // Add action buttons for alarms
        if (ALARM_CHANNEL_ID.equals(channelId)) {
            Intent acknowledgeIntent = new Intent(this, NotificationActionReceiver.class);
            acknowledgeIntent.setAction("ACKNOWLEDGE_ALARM");
            if (data.containsKey("alarm_id")) {
                acknowledgeIntent.putExtra("alarm_id", data.get("alarm_id"));
            }

            PendingIntent acknowledgePendingIntent = PendingIntent.getBroadcast(
                this,
                0,
                acknowledgeIntent,
                flags
            );

            notificationBuilder.addAction(
                R.drawable.ic_notification,
                "Acknowledge",
                acknowledgePendingIntent
            );
        }

        NotificationManager notificationManager =
            (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        int notificationId = (int) System.currentTimeMillis();
        notificationManager.notify(notificationId, notificationBuilder.build());
    }

    /**
     * Create notification channels (Android O+)
     */
    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // Default channel
            NotificationChannel defaultChannel = new NotificationChannel(
                DEFAULT_CHANNEL_ID,
                "Default Notifications",
                NotificationManager.IMPORTANCE_HIGH
            );
            defaultChannel.setDescription("Default notification channel");
            defaultChannel.enableVibration(true);

            // Alarm channel
            NotificationChannel alarmChannel = new NotificationChannel(
                ALARM_CHANNEL_ID,
                "Alarms & Alerts",
                NotificationManager.IMPORTANCE_HIGH
            );
            alarmChannel.setDescription("Critical alarms and alerts");
            alarmChannel.enableVibration(true);
            alarmChannel.setVibrationPattern(new long[]{0, 500, 200, 500});

            NotificationManager notificationManager = getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(defaultChannel);
            notificationManager.createNotificationChannel(alarmChannel);
        }
    }

    /**
     * Send token to backend
     */
    private void sendTokenToBackend(String token) {
        // TODO: Implement API call to register device token
        android.util.Log.d(TAG, "Sending token to backend: " + token);
    }
}

/**
 * Notification Action Receiver
 * Handles notification action button clicks
 */
class NotificationActionReceiver extends android.content.BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        android.util.Log.d("NotificationAction", "Action: " + action);

        if ("ACKNOWLEDGE_ALARM".equals(action)) {
            String alarmId = intent.getStringExtra("alarm_id");
            android.util.Log.d("NotificationAction", "Acknowledge alarm: " + alarmId);
            // TODO: Send acknowledge request to backend
        }
    }
}
