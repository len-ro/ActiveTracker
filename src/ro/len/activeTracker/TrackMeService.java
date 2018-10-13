package ro.len.activeTracker;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Binder;
import android.os.Bundle;
import android.os.IBinder;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.telephony.TelephonyManager;
import android.text.TextUtils;
import android.util.Log;
import android.widget.Toast;

public class TrackMeService extends Service implements LocationListener{
	private static final String TRACKME_URL = "http://www.len.ro/activeTracker/trackMe.py";
	
	private static final String TAG = "ActiveTracker";
	
	private LocationManager locationManager;
	private DecimalFormat decimalFormat;
	private HttpClient httpClient;
	private PowerManager powerManager;
	private WakeLock wakeLock;
	private static boolean showDebug = false;
	private static String trackCode = null;
	private static Integer eventId = null;
	
	private static int MIN_UPDATE_TIME = 15 * 1000; //15 seconds
	private static float MIN_UPDATE_DST = 10f; //10 meters
	private static float MAX_ACCURACY = 30f; //30 meters
	private static float TWO_MINUTES = 2 * 60 * 1000; // 2 min
	
	private Location lastKnownLocation;
	private Vector<Location> previousBadLocations = new Vector<Location>();
	
	private String imei = null;
	private boolean sentImei = false;

	@Override
	public void onCreate() {
		super.onCreate();
		showNotification();
		startTrackingService();
	}
	
	private void startTrackingService(){
		sentImei = false;
		
		//ensure it stays on
		powerManager = (PowerManager) getSystemService(POWER_SERVICE);
		wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, getClass().getName());
		wakeLock.acquire();
		
		log(getString(R.string.statusWaitingForLocation), true);
		
		locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
		locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, MIN_UPDATE_TIME, MIN_UPDATE_DST, this);
		//locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, MIN_UPDATE_TIME, MIN_UPDATE_DST, trackMeGpsListener);
		
		decimalFormat = new DecimalFormat("#0.######");
		httpClient = new DefaultHttpClient();

		previousBadLocations.clear();
		
		TelephonyManager telephonyManager = (TelephonyManager)getSystemService(Context.TELEPHONY_SERVICE); 
		imei = telephonyManager.getDeviceId();
		
		lastKnownLocation = locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
		Location location = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);
		if(isBetterLocation(location, lastKnownLocation)){
			lastKnownLocation = location;
		}

		if(lastKnownLocation != null){
			postLocation(lastKnownLocation, true);
		}
	}
	
	private Notification notification = null;
	private PendingIntent notificationIntent = null;
	private NotificationManager notificationManager = null;
	
	/**
	 * Show a notification while this service is running.
	 */
	private void showNotification() {
		CharSequence text = getText(R.string.local_service_started);

		// Set the icon, scrolling text and timestamp
		notification = new Notification(R.drawable.icon, text, System.currentTimeMillis());

		// The PendingIntent to launch our activity if the user selects this notification
		Intent openActivityIntent = new Intent(this, TrackMeActivity.class);
		openActivityIntent.setAction(Intent.ACTION_MAIN);
	    openActivityIntent.addCategory(Intent.CATEGORY_LAUNCHER);
	    
		notificationIntent = PendingIntent.getActivity(this, 0, openActivityIntent, 0);
		// Set the info for the views that show in the notification panel.
		notification.setLatestEventInfo(this, getText(R.string.service_name), text, notificationIntent);

		// Send the notification
		notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
		// notificationManager.notify(R.string.notification_id, notification);
		startForeground(R.string.notification_id, notification);
	}
	
	private void log(String message){
		log(message, false);
	}
			
	private void log(String message, boolean notify){
		Log.i(TAG, message);
		
		if (showDebug || notify) Toast.makeText(getBaseContext(), message, Toast.LENGTH_SHORT).show();

		if (notify){
			notification.setLatestEventInfo(this, getText(R.string.service_name), message, notificationIntent);
			notificationManager.notify(R.string.notification_id, notification);
		}
	}

	@Override
	public void onDestroy() {
		super.onDestroy();
		stopTrackingService();

		// Cancel the persistent notification.
		// notificationManager.cancel(R.string.local_service_started);

		// Tell the user we stopped.
		Toast.makeText(this, R.string.local_service_stopped, Toast.LENGTH_SHORT).show();
	}
	
	private void stopTrackingService(){
		if(locationManager != null){
			locationManager.removeUpdates(this);
		}
		wakeLock.release();
	}

	@Override
	public void onLocationChanged(Location location) {
		log("Update received");
		location = checkLocation(location);
		if(location != null){
			postLocation(location, false);
			lastKnownLocation = location;
		}		
	}

	/**
	 * Some common sense checks on a new location update
	 * @param proposedLocation
	 * @return
	 */
	private Location checkLocation(Location proposedLocation) {
		if (proposedLocation != null && (proposedLocation.getLatitude() == 0.0d || proposedLocation.getLongitude() == 0.0d)){
			log("Bad location: 0 lat or lon");
			return null;
		}

		if (proposedLocation != null && proposedLocation.getAccuracy() > MAX_ACCURACY) {
			log(String.format("Bad location: accuracy %f > %f", proposedLocation.getAccuracy(), MAX_ACCURACY));
			proposedLocation = addBadLocation(proposedLocation);
		}

		// Do not log a waypoint which might be on any side of the previous waypoint
		if (proposedLocation != null && lastKnownLocation != null && proposedLocation.getAccuracy() > lastKnownLocation.distanceTo(proposedLocation)) {
			log(String.format("Bad location: accuracy %f > distance %f", proposedLocation.getAccuracy(), lastKnownLocation.distanceTo(proposedLocation)));
			proposedLocation = addBadLocation(proposedLocation);
		}

		// Older bad locations will not be needed
		if (proposedLocation != null){
			previousBadLocations.clear();
		}
		return proposedLocation;
	}
	
	private Location addBadLocation(Location location){
		previousBadLocations.add(location);
		if (previousBadLocations.size() < 3){
			location = null;
		}else{
			log("Choosing the least bad location.");
			Location best = previousBadLocations.lastElement();
			for (Location l : previousBadLocations){
				if (l.hasAccuracy() && best.hasAccuracy() && l.getAccuracy() < best.getAccuracy()){
					best = l;
				}else{
					if (l.hasAccuracy() && !best.hasAccuracy()){
						best = l;
					}
				}
			}
			synchronized (previousBadLocations){
				previousBadLocations.clear();
			}
			location = best;
		}
		log("addBadLocation: " + location);
		return location;
	}
	
	private boolean minUpdateSize = true;
	
	private void postLocation(Location location, boolean lastKnown) {
		if(location!=null){
			try {
				HttpPost post = new HttpPost(TRACKME_URL);
				List<NameValuePair> params = new ArrayList<NameValuePair>();
				if(!sentImei && !TextUtils.isEmpty(imei)){
					params.add(new BasicNameValuePair("phoneId", imei));
					sentImei = true;
				}
				String latitude = decimalFormat.format(location.getLatitude());
				String longitude = decimalFormat.format(location.getLongitude());
				String altitude = decimalFormat.format(location.getAltitude());
				String accuracy = decimalFormat.format(location.getAccuracy());
				String time = new Long(location.getTime()).toString();
				if(minUpdateSize){
					StringBuilder t = new StringBuilder();
					t.append(eventId.toString()).append("|");
					t.append(trackCode).append("|");
					t.append(latitude).append("|");
					t.append(longitude).append("|");
					t.append(altitude).append("|");
					t.append(accuracy).append("|");
					t.append(time);
					params.add(new BasicNameValuePair("t", t.toString()));
				}else{
					params.add(new BasicNameValuePair("lat", latitude));
					params.add(new BasicNameValuePair("lon", longitude));
					params.add(new BasicNameValuePair("alt", altitude));
					params.add(new BasicNameValuePair("accuracy", accuracy));
					params.add(new BasicNameValuePair("time", time));
					params.add(new BasicNameValuePair("trackCode", trackCode));
					params.add(new BasicNameValuePair("eventId", eventId.toString()));
				}
				post.setEntity(new UrlEncodedFormEntity(params));
				HttpResponse response = httpClient.execute(post);
				response.getEntity().consumeContent();
				
				if(lastKnown){
					log(getString(R.string.statusSentLastKnown), true);
				}else{
					StringBuilder msg = new StringBuilder();
					msg.append(latitude).append("/").append(longitude);
					log(getString(R.string.statusTrackedLocation) + ": " + msg.toString(), true);
				}
			} catch (Exception e) {
				log("error sending location: " + e.getMessage());
				log("Could not update location", true);
			}
		}
	}

	@Override
	public void onProviderDisabled(String provider) {
		if(LocationManager.GPS_PROVIDER.equals(provider)){
			/*AlertDialog.Builder builder = new AlertDialog.Builder(getBaseContext());
			builder.setTitle(getString(R.string.gpsOffTitle));
			builder.setMessage(getString(R.string.gpsOffMessage));
			builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
				public void onClick(DialogInterface dialogInterface, int i) {
					// Show location settings when the user acknowledges the alert dialog
					Intent intent = new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS);
					intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
					startActivity(intent);
				}
			});
			Dialog alertDialog = builder.create();
			alertDialog.setCanceledOnTouchOutside(false);
			alertDialog.show();*/

			Toast.makeText(getApplicationContext(), getString(R.string.gpsOffMessage), Toast.LENGTH_LONG).show();
			//bring up the GPS settings 
			Intent intent = new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS);
			intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
			startActivity(intent);
		}
	}

	@Override
	public void onProviderEnabled(String provider) {
		// TODO Auto-generated method stub
	}

	@Override
	public void onStatusChanged(String provider, int status, Bundle extras) {
		// TODO Auto-generated method stub
	}

	/** Determines whether one Location reading is better than the current Location fix
	 * @param location  The new Location that you want to evaluate
	 * @param currentBestLocation  The current Location fix, to which you want to compare the new one
	 */
	protected boolean isBetterLocation(Location location, Location currentBestLocation) {
		if (currentBestLocation == null) {
			// A new location is always better than no location
			return true;
		}

		if (location == null){
			return false;
		}

		// Check whether the new location fix is newer or older
		long timeDelta = location.getTime() - currentBestLocation.getTime();
		boolean isSignificantlyNewer = timeDelta > TWO_MINUTES;
		boolean isSignificantlyOlder = timeDelta < -TWO_MINUTES;
		boolean isNewer = timeDelta > 0;

		// If it's been more than two minutes since the current location, use the new location
		// because the user has likely moved
		if (isSignificantlyNewer) {
			return true;
			// If the new location is more than two minutes older, it must be worse
		} else if (isSignificantlyOlder) {
			return false;
		}

		// Check whether the new location fix is more or less accurate
		int accuracyDelta = (int) (location.getAccuracy() - currentBestLocation.getAccuracy());
		boolean isLessAccurate = accuracyDelta > 0;
		boolean isMoreAccurate = accuracyDelta < 0;
		boolean isSignificantlyLessAccurate = accuracyDelta > 200;

		// Check if the old and new location are from the same provider
		boolean isFromSameProvider = isSameProvider(location.getProvider(),
				currentBestLocation.getProvider());

		// Determine location quality using a combination of timeliness and accuracy
		if (isMoreAccurate) {
			return true;
		} else if (isNewer && !isLessAccurate) {
			return true;
		} else if (isNewer && !isSignificantlyLessAccurate && isFromSameProvider) {
			return true;
		}
		return false;
	}

	/** Checks whether two providers are the same */
	private boolean isSameProvider(String provider1, String provider2) {
		if (provider1 == null) {
			return provider2 == null;
		}
		return provider1.equals(provider2);
	}

	// This is the object that receives interactions from clients. See
	// RemoteService for a more complete example.
	private final IBinder binder = new LocalBinder();

	/**
	 * Class for clients to access. Because we know this service always runs in
	 * the same process as its clients, we don't need to deal with IPC.
	 */
	public class LocalBinder extends Binder {
		TrackMeService getService() {
			return TrackMeService.this;
		}
	}

	@Override
	public IBinder onBind(Intent intent) {
		return binder;
	}

	public static boolean isShowDebug() {
		return showDebug;
	}

	public static void setShowDebug(boolean showDebug) {
		TrackMeService.showDebug = showDebug;
	}

	/**
	 * @return the trackCode
	 */
	public static String getTrackCode() {
		return trackCode;
	}
	
	/**
	 * @return the eventId
	 */
	public static Integer getEventId() {
		return eventId;
	}

	/**
	 * @param trackCode the trackCode to set
	 */
	public static void setTrackingData(int eventId, String trackCode) {
		TrackMeService.trackCode = trackCode;
		TrackMeService.eventId = eventId;
	}
}
