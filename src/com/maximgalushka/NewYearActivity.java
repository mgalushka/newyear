package com.maximgalushka;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesUtil;
import com.google.android.gms.gcm.GoogleCloudMessaging;
import com.google.gson.Gson;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;

import java.io.IOException;

public class NewYearActivity extends Activity {

  String PUSH_SERVICE_REGISTRATION = "https://api.backendless.com/v1/messaging/registrations";

  String REGISTER_DEVICE = "http://192.168.1.103/omxplayer-web-controls-php/open.php?path=";
  String ROOT = "http://192.168.1.103/omxplayer-web-controls-php/open.php?path=";

  // Google Project Number: 306055063211
  String SENDER_ID = "306055063211";


  String EXTRA_MESSAGE = "message";
  String PROPERTY_REG_ID = "registration_id";
  String PROPERTY_APP_VERSION = "appVersion";

  int PLAY_SERVICES_RESOLUTION_REQUEST = 9000;

  private static final String TAG = "NewYearActivity";
  private static GoogleCloudMessaging gcm;
  private static String regid;
  private static String registrationStatus;
  private static Context context;

  private Button activateButton;

  /**
   * Called when the activity is first created.
   */
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    this.activateButton = (Button) this.findViewById(R.id.activate);
    this.activateButton.setOnClickListener(v -> {
      Log.d(TAG, "Registering device!");
      retrieveRegistrationId();
    });
  }

  void retrieveRegistrationId() {
    if (checkPlayServices()) {
      gcm = GoogleCloudMessaging.getInstance(this);
      regid = getRegistrationId(this.getApplicationContext());

      Log.d(TAG, "RegistrationId: " + regid);
      registrationStatus = regid;

      if (regid.isEmpty()) {
        registerInBackground();
      }
    }
  }


  boolean checkPlayServices() {
    int resultCode = GooglePlayServicesUtil.isGooglePlayServicesAvailable(this);
    if (resultCode != ConnectionResult.SUCCESS) {
      if (GooglePlayServicesUtil.isUserRecoverableError(resultCode)) {
        GooglePlayServicesUtil.getErrorDialog(
          resultCode,
          this,
          PLAY_SERVICES_RESOLUTION_REQUEST
        ).show();
      } else {
        Log.d(TAG, "This device is not supported.");
      }
      return false;
    }
    return true;
  }

  String getRegistrationId(Context context) {
    final SharedPreferences prefs = getGCMPreferences(context);
    String registrationId = prefs.getString(PROPERTY_REG_ID, "");
    if (registrationId.isEmpty()) {
      Log.d(TAG, "Registration not found.");
      return "";
    }
    // Check if app was updated; if so, it must clear the registration ID
    // since the existing regID is not guaranteed to work with the new
    // app version.
    int registeredVersion = prefs.getInt(PROPERTY_APP_VERSION, Integer.MIN_VALUE);
    int currentVersion = getAppVersion(context);
    if (registeredVersion != currentVersion) {
      Log.d(TAG, "App version changed.");
      return "";
    }
    return registrationId;
  }

  private SharedPreferences getGCMPreferences(Context context) {
    // This sample app persists the registration ID in shared preferences, but
    // how you store the regID in your app is up to you.
    return this.getSharedPreferences("NewYear", Activity.MODE_PRIVATE);
  }

  void registerInBackground() {
    AsyncTask a = new AsyncTask() {

      protected String doInBackground(Object... params) {

        String msg = "";
        Log.d(TAG, "start background registration");
        try {
          if (gcm == null) {
            Log.d(TAG, "retrieving GCM instance");
            gcm = GoogleCloudMessaging.getInstance(context);
            Log.d(TAG, "GCM instance retrieved");
          }
          Log.d(TAG, "Requesting registration");
          regid = gcm.register(SENDER_ID);
          msg = "Device registered, registration ID=" + regid;

          Log.d(TAG, msg);

          registrationStatus = msg;

          // You should send the registration ID to your server over HTTP,
          // so it can use GCM/HTTP or CCS to send messages to your app.
          // The request to your server should be authenticated if your app
          // is using accounts.
          sendRegistrationIdToBackend();

          // For this demo: we don't need to send it because the device
          // will send upstream messages to a server that echo back the
          // message using the 'from' address in the message.

          // Persist the regID - no need to register again.
          storeRegistrationId(context, regid);
        } catch (IOException ex) {
          msg = "Error :" + ex.getMessage();
          // If there is an error, don't just keep trying to register.
          // Require the user to click a button again, or perform
          // exponential back-off.

          Log.d(TAG, "Error: " + msg);
          registrationStatus = msg;
        }
        return msg;
      }

      protected void onPostExecute(String msg) {
        Log.d(TAG, msg);
        registrationStatus = msg;
      }
    };
    a.execute(null, null, null);
  }


  private void sendRegistrationIdToBackend() {
    // Your implementation here.
    // post to service
    Log.d(TAG, "here we need to send registration key to backend");
  }

  private static int getAppVersion(Context context) {
    try {
      PackageInfo packageInfo = context.getPackageManager()
                                       .getPackageInfo(context.getPackageName(), 0);
      return packageInfo.versionCode;
    } catch (Exception e) {
      // should never happen
      throw new RuntimeException("Could not get package name: " + e);
    }
  }

  private void storeRegistrationId(Context context, String regId) {
    final SharedPreferences prefs = getGCMPreferences(context);
    int appVersion = getAppVersion(context);
    Log.d(TAG, "Saving regId on app version " + appVersion);
    SharedPreferences.Editor editor = prefs.edit();
    editor.putString(PROPERTY_REG_ID, regId);
    editor.putInt(PROPERTY_APP_VERSION, appVersion);
    editor.commit();
  }


  void sendToServer(String command) {
    try {
      DefaultHttpClient httpClient = new DefaultHttpClient();
      Log.d(TAG, "Execute command: " + command);
      HttpPost httpPost = new HttpPost(ROOT);
      HttpParams postParams = new BasicHttpParams();
      postParams.setParameter("act", command);
      postParams.setParameter("arg", "undefined");
      httpPost.setParams(postParams);

      HttpResponse response = httpClient.execute(httpPost);
      HttpEntity entity = response.getEntity();

      Gson gson = new Gson(); // Or use new GsonBuilder().create();

      Log.d(TAG, "----------------------------------------");
      Log.d(TAG, String.valueOf(response.getStatusLine()));
      Log.d(TAG, "----------------------------------------");

      String json = EntityUtils.toString(entity);
      Log.d(TAG, "json = " + json);

      //if ( entity != null ) entity.writeTo( System.out );
      //if ( entity != null ) entity.consumeContent();
    } catch (IOException io) {
      io.printStackTrace();
    }
  }

}
