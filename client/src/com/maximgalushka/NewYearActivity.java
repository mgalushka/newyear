package com.maximgalushka;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GoogleApiAvailability;
import com.google.android.gms.gcm.GoogleCloudMessaging;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class NewYearActivity extends Activity {

  private static final String ROOT = "http://api.lightbot.co:8080";

  private static final String SAVE_KEY = "/save-key";
  private static final String GET_KEY = "/get-key";

  // Google Project Number: 306055063211
  String SENDER_ID = "306055063211";

  String PROPERTY_REG_ID = "registration_id";
  String PROPERTY_DEVICE_ID = "device_id";
  String PROPERTY_APP_VERSION = "appVersion";

  int PLAY_SERVICES_RESOLUTION_REQUEST = 9000;

  private static final String TAG = "NewYearActivity";
  private static GoogleCloudMessaging gcm;
  private static String regid;

  /**
   * Called when the activity is first created.
   */
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    Button activateButton = (Button) this.findViewById(R.id.activate);
    activateButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        Log.d(TAG, "Registering device!");
        NewYearActivity.this.retrieveRegistrationId();
      }
    });
  }

  void retrieveRegistrationId() {
    Context context = this.getApplicationContext();
    if (checkPlayServices(context)) {
      gcm = GoogleCloudMessaging.getInstance(this);
      regid = getRegistrationId();

      Log.d(TAG, "RegistrationId: " + regid);

      if (regid.isEmpty()) {
        registerInBackground(context);
      }
    }
  }


  boolean checkPlayServices(Context context) {
    GoogleApiAvailability api = GoogleApiAvailability.getInstance();
    int resultCode = api.isGooglePlayServicesAvailable(context);
    if (resultCode != ConnectionResult.SUCCESS) {
      if (api.isUserResolvableError(resultCode)) {
        api.getErrorDialog(
          this,
          resultCode,
          PLAY_SERVICES_RESOLUTION_REQUEST
        ).show();
      } else {
        Log.d(TAG, "This device is not supported.");
      }
      return false;
    }
    return true;
  }

  String getRegistrationId() {
    final SharedPreferences prefs = getGCMPreferences();
    String registrationId = prefs.getString(PROPERTY_REG_ID, "");
    String deviceId = prefs.getString(PROPERTY_DEVICE_ID, "");
    if (registrationId.isEmpty()) {
      Log.w(TAG, "Registration not found. Trying to get registration id from server.");

      // check if device id is in preferences and try to get registration id from server:
      if (deviceId.isEmpty()) {
        Log.w(TAG, "Device id not found on server. Need to generate new id.");
        return "";
      } else {
        registrationId = sendToServer(GET_KEY, deviceId, null);
        Log.d(TAG, String.format("Registration id found on server: %s", registrationId));
      }
    } else {
      Log.d(TAG, String.format("Registration id is found in storage %s. Save it on server.", registrationId));
      sendToServer(SAVE_KEY, deviceId, registrationId);
    }
    // Check if app was updated; if so, it must clear the registration ID
    // since the existing regID is not guaranteed to work with the new
    // app version.
    int registeredVersion = prefs.getInt(PROPERTY_APP_VERSION, Integer.MIN_VALUE);
    int currentVersion = getAppVersion();
    if (registeredVersion != currentVersion) {
      Log.w(TAG, "App version changed. Need to generate new id.");
      return "";
    }
    return registrationId;
  }

  private SharedPreferences getGCMPreferences() {
    // This sample app persists the registration ID in shared preferences, but
    // how you store the regID in your app is up to you.
    return this.getSharedPreferences("NewYear", Activity.MODE_PRIVATE);
  }

  @SuppressWarnings("unchecked")
  void registerInBackground(final Context context) {
    AsyncTask a = new AsyncTask() {

      protected String doInBackground(Object... params) {

        String msg;
        Log.d(TAG, "start background registration");
        try {
          if (gcm == null) {
            Log.d(TAG, "retrieving GCM instance");
            gcm = GoogleCloudMessaging.getInstance(context);
            Log.d(TAG, "GCM instance retrieved");
          }
          Log.d(TAG, "Requesting registration");
          regid = gcm.register(SENDER_ID);
          msg = "Device registered, registration ID = " + regid;

          Log.d(TAG, msg);

          // You should send the registration ID to your server over HTTP,
          // so it can use GCM/HTTP or CCS to send messages to your app.
          // The request to your server should be authenticated if your app
          // is using accounts.
          sendRegistrationIdToBackend(regid);

          // For this demo: we don't need to send it because the device
          // will send upstream messages to a server that echo back the
          // message using the 'from' address in the message.

          // Persist the regID - no need to register again.
          storeRegistrationId(regid);
        } catch (IOException ex) {
          msg = "Error :" + ex.getMessage();
          // If there is an error, don't just keep trying to register.
          // Require the user to click a button again, or perform
          // exponential back-off.

          Log.d(TAG, "Error: " + msg);
        }
        return msg;
      }

    };
    a.execute();
  }


  private void sendRegistrationIdToBackend(String registrationId) {
    // generate unique device id and store it if it is not stored already
    final SharedPreferences prefs = getGCMPreferences();
    String deviceId = prefs.getString(PROPERTY_DEVICE_ID, "");
    if (deviceId.isEmpty()) {
      deviceId = UUID.randomUUID().toString();
      SharedPreferences.Editor editor = prefs.edit();
      editor.putString(PROPERTY_DEVICE_ID, deviceId);
      editor.apply();
    }
    Log.d(TAG, String.format("Device id: %s", deviceId));
    // post to service
    sendToServer(SAVE_KEY, deviceId, registrationId);
    Log.d(TAG, "Sent registration id to server");
  }

  private static int getAppVersion() {
    // TODO: hard-code - remove this
    return 1;
  }

  private void storeRegistrationId(String regId) {
    final SharedPreferences prefs = getGCMPreferences();
    int appVersion = getAppVersion();
    Log.d(TAG, "Saving regId on app version " + appVersion);
    SharedPreferences.Editor editor = prefs.edit();
    editor.putString(PROPERTY_REG_ID, regId);
    editor.putInt(PROPERTY_APP_VERSION, appVersion);
    editor.apply();
  }

  @SuppressWarnings("unchecked")
  String sendToServer(final String action, final String deviceId, final String key) {
    AsyncTask a = new AsyncTask() {

      protected String doInBackground(Object... params) {

        try {
          DefaultHttpClient httpClient = new DefaultHttpClient();
          Log.d(TAG, "Execute request on server: " + action);

          HttpPost httpPost = new HttpPost(String.format("%s%s", ROOT, action));

          List<NameValuePair> nvps = new ArrayList<>();
          nvps.add(new BasicNameValuePair("device", deviceId));

          if (key != null) {
            nvps.add(new BasicNameValuePair("key", key));
          }

          httpPost.setEntity(new UrlEncodedFormEntity(nvps, "UTF-8"));

          HttpResponse response = httpClient.execute(httpPost);
          HttpEntity entity = response.getEntity();

          // TODO: thing about protocol between client and server
          //Gson gson = new Gson(); // Or use new GsonBuilder().create();

          Log.d(TAG, "----------------------------------------");
          Log.d(TAG, String.valueOf(response.getStatusLine()));
          Log.d(TAG, "----------------------------------------");

          String result = EntityUtils.toString(entity);
          Log.d(TAG, "result = " + result);

          // TODO: think about protocol as this looks like a hack
          if ("ERROR".equalsIgnoreCase(result)) {
            return "";
          }
          return result;
        } catch (IOException io) {
          io.printStackTrace();
        }

        return "";
      }
    };

    a.execute();
    try {
      return (String) a.get(30, TimeUnit.SECONDS);
    } catch (Exception e) {
      e.printStackTrace();
    }
    return null;
  }



}
