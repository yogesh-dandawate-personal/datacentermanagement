/**
 * iOS Notification Service
 *
 * Handles:
 * - Push notification delivery
 * - Rich notifications (images, actions)
 * - Notification content modification
 * - Badge management
 */

import UserNotifications
import Firebase

class NotificationService: NSObject, UNUserNotificationCenterDelegate {

  // MARK: - Singleton
  static let shared = NotificationService()

  private override init() {
    super.init()
  }

  // MARK: - Setup
  func setup() {
    UNUserNotificationCenter.current().delegate = self

    // Register notification categories
    registerNotificationCategories()

    // Request authorization
    requestAuthorization()
  }

  // MARK: - Authorization
  func requestAuthorization() {
    let authOptions: UNAuthorizationOptions = [.alert, .badge, .sound]
    UNUserNotificationCenter.current().requestAuthorization(options: authOptions) { granted, error in
      if granted {
        print("Notification permission granted")
        DispatchQueue.main.async {
          UIApplication.shared.registerForRemoteNotifications()
        }
      } else {
        print("Notification permission denied: \(error?.localizedDescription ?? "unknown error")")
      }
    }
  }

  // MARK: - Categories
  func registerNotificationCategories() {
    // Alarm notification actions
    let acknowledgeAction = UNNotificationAction(
      identifier: "ACKNOWLEDGE_ACTION",
      title: "Acknowledge",
      options: [.foreground]
    )

    let viewDetailsAction = UNNotificationAction(
      identifier: "VIEW_DETAILS_ACTION",
      title: "View Details",
      options: [.foreground]
    )

    let alarmCategory = UNNotificationCategory(
      identifier: "ALARM_CATEGORY",
      actions: [acknowledgeAction, viewDetailsAction],
      intentIdentifiers: [],
      options: []
    )

    // Energy threshold notification actions
    let viewEnergyAction = UNNotificationAction(
      identifier: "VIEW_ENERGY_ACTION",
      title: "View Energy",
      options: [.foreground]
    )

    let energyCategory = UNNotificationCategory(
      identifier: "ENERGY_CATEGORY",
      actions: [viewEnergyAction],
      intentIdentifiers: [],
      options: []
    )

    UNUserNotificationCenter.current().setNotificationCategories([alarmCategory, energyCategory])
  }

  // MARK: - UNUserNotificationCenterDelegate

  // Called when notification arrives while app is in foreground
  func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    willPresent notification: UNNotification,
    withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
  ) {
    let userInfo = notification.request.content.userInfo
    print("Notification received (foreground): \(userInfo)")

    // Display notification even when app is in foreground
    completionHandler([.banner, .sound, .badge])
  }

  // Called when user taps notification
  func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void
  ) {
    let userInfo = response.notification.request.content.userInfo
    let actionIdentifier = response.actionIdentifier

    print("Notification action: \(actionIdentifier)")
    print("Notification data: \(userInfo)")

    // Handle actions
    switch actionIdentifier {
    case "ACKNOWLEDGE_ACTION":
      handleAcknowledgeAction(userInfo: userInfo)
    case "VIEW_DETAILS_ACTION":
      handleViewDetailsAction(userInfo: userInfo)
    case "VIEW_ENERGY_ACTION":
      handleViewEnergyAction(userInfo: userInfo)
    case UNNotificationDefaultActionIdentifier:
      // User tapped notification
      handleDefaultAction(userInfo: userInfo)
    default:
      break
    }

    completionHandler()
  }

  // MARK: - Action Handlers

  func handleAcknowledgeAction(userInfo: [AnyHashable: Any]) {
    if let alarmId = userInfo["alarm_id"] as? String {
      // Send acknowledge request to backend
      print("Acknowledging alarm: \(alarmId)")
      // TODO: Call API to acknowledge alarm
    }
  }

  func handleViewDetailsAction(userInfo: [AnyHashable: Any]) {
    // Navigate to alarm details
    print("Viewing alarm details")
    // TODO: Deep link to alarm screen
  }

  func handleViewEnergyAction(userInfo: [AnyHashable: Any]) {
    // Navigate to energy screen
    print("Viewing energy metrics")
    // TODO: Deep link to energy screen
  }

  func handleDefaultAction(userInfo: [AnyHashable: Any]) {
    // Handle default tap action
    print("Notification tapped")

    if let notificationType = userInfo["type"] as? String {
      switch notificationType {
      case "energy_threshold":
        // Navigate to energy screen
        print("Navigate to energy screen")
      case "emission_alert":
        // Navigate to emissions screen
        print("Navigate to emissions screen")
      case "system_warning":
        // Navigate to alarms screen
        print("Navigate to alarms screen")
      default:
        break
      }
    }
  }

  // MARK: - Badge Management

  func updateBadge(count: Int) {
    DispatchQueue.main.async {
      UIApplication.shared.applicationIconBadgeNumber = count
    }
  }

  func clearBadge() {
    updateBadge(count: 0)
  }

  // MARK: - Local Notifications

  func scheduleLocalNotification(
    title: String,
    body: String,
    categoryIdentifier: String,
    userInfo: [AnyHashable: Any],
    trigger: UNNotificationTrigger? = nil
  ) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body
    content.sound = .default
    content.categoryIdentifier = categoryIdentifier
    content.userInfo = userInfo

    let identifier = UUID().uuidString
    let request = UNNotificationRequest(
      identifier: identifier,
      content: content,
      trigger: trigger
    )

    UNUserNotificationCenter.current().add(request) { error in
      if let error = error {
        print("Failed to schedule notification: \(error.localizedDescription)")
      } else {
        print("Notification scheduled: \(identifier)")
      }
    }
  }
}
