package com.maximgalushka.service;

import android.app.IntentService;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.v4.app.NotificationCompat;
import android.util.Log;
import com.google.android.gms.gcm.GoogleCloudMessaging;
import com.maximgalushka.NewYearActivity;
import com.maximgalushka.R;

public class GcmIntentService extends IntentService {
  private static final String TAG = "GcmIntentService";

  public static final int NOTIFICATION_ID = 1;
  private NotificationManager mNotificationManager;
  NotificationCompat.Builder builder;

  public GcmIntentService() {
    super("GcmIntentService");
  }

  @Override
  protected void onHandleIntent(Intent intent) {
    Bundle extras = intent.getExtras();
    GoogleCloudMessaging gcm = GoogleCloudMessaging.getInstance(this);
    // The getMessageType() intent parameter must be the intent you received
    // in your BroadcastReceiver.
    String messageType = gcm.getMessageType(intent);
    Log.d(TAG, "!!! Received GCM message type: " + messageType);
    if (!extras.isEmpty()) {  // has effect of unparcelling Bundle
      /*
       * Filter messages based on message type. Since it is likely that GCM
       * will be extended in the future with new message types, just ignore
       * any message types you're not interested in, or that you don't
       * recognize.
       */
      if (GoogleCloudMessaging.
        MESSAGE_TYPE_SEND_ERROR.equals(messageType)) {
        sendNotification("Send error: " + extras.toString());
      } else if (GoogleCloudMessaging.
        MESSAGE_TYPE_DELETED.equals(messageType)) {
        sendNotification("Deleted messages on server: " +
                           extras.toString());
        // If it's a regular GCM message, do some work.
      } else if (GoogleCloudMessaging.
        MESSAGE_TYPE_MESSAGE.equals(messageType)) {
        // This loop represents the service doing some work.
        for (int i = 0; i < 5; i++) {
          Log.d(TAG, "Working... " + (i + 1)
            + "/5 @ " + SystemClock.elapsedRealtime());
          try {
            Thread.sleep(5000);
          } catch (InterruptedException e) {
          }
        }
        Log.d(TAG, "Completed work @ " + SystemClock.elapsedRealtime());
        // Post notification of received message.
        String messageText = extras.getString("text");
        sendNotification(messageText);
        Log.d(TAG, "Received: " + messageText);
      }
    }
    // Release the wake lock provided by the WakefulBroadcastReceiver.
    GcmBroadcastReceiver.completeWakefulIntent(intent);
  }

  // Put the message into a notification and post it.
  // This is just one simple example of what you might choose to do with
  // a GCM message.
  @SuppressWarnings("ResourceType")
  private void sendNotification(String msg) {
    mNotificationManager = (NotificationManager)
      this.getSystemService(Context.NOTIFICATION_SERVICE);

    NotificationCompat.Builder mBuilder =
      new NotificationCompat.Builder(this)
        .setSmallIcon(R.drawable.ic_launcher)
        .setContentTitle("NewYear")
        .setStyle(new NotificationCompat.BigTextStyle()
                    .bigText(msg))
        .setContentText(msg)
        .setAutoCancel(true);

    // pending intent is redirection using the deep-link
    Intent resultIntent = new Intent(Intent.ACTION_VIEW);
    resultIntent.setData(Uri.parse(String.format("https://en.wikipedia.org/wiki/%s", msg)));

    PendingIntent pending = PendingIntent.getActivity(
      this, 0, resultIntent, Intent.FLAG_ACTIVITY_NEW_TASK);
    mBuilder.setContentIntent(pending);

    mNotificationManager.notify(NOTIFICATION_ID, mBuilder.build());
  }
}

