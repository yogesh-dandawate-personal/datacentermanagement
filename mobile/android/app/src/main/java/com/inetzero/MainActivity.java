package com.inetzero;

import android.os.Bundle;
import com.facebook.react.ReactActivity;
import com.facebook.react.ReactActivityDelegate;
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint;
import com.facebook.react.defaults.DefaultReactActivityDelegate;

/**
 * Main Activity for iNetZero Mobile App
 */
public class MainActivity extends ReactActivity {

  /**
   * Returns the name of the main component registered from JavaScript.
   * This is used to schedule rendering of the component.
   */
  @Override
  protected String getMainComponentName() {
    return "iNetZero";
  }

  /**
   * Returns the instance of the {@link ReactActivityDelegate}. Here we use a util class {@link
   * DefaultReactActivityDelegate} which allows you to easily enable Fabric and Concurrent React
   * (aka React 18) with two boolean flags.
   */
  @Override
  protected ReactActivityDelegate createReactActivityDelegate() {
    return new DefaultReactActivityDelegate(
        this,
        getMainComponentName(),
        // If you opted-in for the New Architecture, we enable the Fabric Renderer.
        DefaultNewArchitectureEntryPoint.getFabricEnabled());
  }

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    // Initialize deep linking
    handleDeepLink();

    // Request notification permissions (Android 13+)
    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
      requestPermissions(
          new String[]{android.Manifest.permission.POST_NOTIFICATIONS},
          1
      );
    }
  }

  /**
   * Handle deep link intents
   */
  private void handleDeepLink() {
    android.content.Intent intent = getIntent();
    String action = intent.getAction();
    android.net.Uri data = intent.getData();

    if (android.content.Intent.ACTION_VIEW.equals(action) && data != null) {
      String scheme = data.getScheme();
      String host = data.getHost();
      String path = data.getPath();

      android.util.Log.d("MainActivity", "Deep link: " + data.toString());

      // Pass to React Native
      // TODO: Send event to React Native
    }
  }

  @Override
  public void onNewIntent(android.content.Intent intent) {
    super.onNewIntent(intent);
    setIntent(intent);
    handleDeepLink();
  }
}
