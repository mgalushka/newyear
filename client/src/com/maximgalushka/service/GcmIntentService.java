package com.maximgalushka.service;

import android.app.IntentService;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.support.v4.app.NotificationCompat;
import android.util.Log;
import com.google.android.gms.gcm.GoogleCloudMessaging;
import com.maximgalushka.NewYearActivity;
import com.maximgalushka.R;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class GcmIntentService extends IntentService {
  private static final String TAG = "GcmIntentService";

  private static int NOTIFICATION_ID = 1;
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
      if (GoogleCloudMessaging.MESSAGE_TYPE_MESSAGE.equals(messageType)) {
        // Post notification of received message.
        String messageText = extras.getString("text");
        String[] countries = extras.getString("countries").split(",");
        String[] cities = extras.getString("cities").split(",");
        List<String> all = new ArrayList<>();
        all.addAll(Arrays.asList(countries));
        all.addAll(Arrays.asList(cities));
        Collections.shuffle(all);

        sendNotification(messageText, all.subList(0, Math.min(all.size(), 5)));
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
  private void sendNotification(String msg, List<String> countries) {
    // pending intent is redirection using the deep-link
    Intent resultIntent = new Intent(Intent.ACTION_VIEW);

    // redirect to 1st country Wikipedia page
    resultIntent.setData(Uri.parse(String.format("https://en.wikipedia.org/wiki/%s", countries.get(0))));

    PendingIntent pending = PendingIntent.getActivity(this, 0, resultIntent, Intent.FLAG_ACTIVITY_NEW_TASK);

    mNotificationManager = (NotificationManager)
      this.getSystemService(Context.NOTIFICATION_SERVICE);

    long[] pattern = {0, 600, 300, 800, 600, 1200};
    Uri defaultSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

    NotificationCompat.Builder mBuilder =
      new NotificationCompat.Builder(this)
        .setSmallIcon(R.drawable.cheers)
        .setContentTitle("NewYear")
        .setStyle(new NotificationCompat.BigTextStyle()
                    .bigText(msg))
        .setContentText(msg)
        .setVibrate(pattern)
        //.setSound(defaultSound)
        .setContentIntent(pending);

    for (String country : countries) {
      Intent actionIntent = new Intent(
        Intent.ACTION_VIEW,
        Uri.parse(String.format("https://en.wikipedia.org/wiki/%s", country))
      );
      PendingIntent actionPendingIntent = PendingIntent.getActivity(this, 0, actionIntent, 0);
      mBuilder.addAction(R.drawable.icon, country, actionPendingIntent);
    }

    mNotificationManager.notify(NOTIFICATION_ID++, mBuilder.build());
  }
}

