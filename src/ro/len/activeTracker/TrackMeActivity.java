package ro.len.activeTracker;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.ActivityManager.RunningServiceInfo;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.text.InputType;
import android.text.TextUtils;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnLongClickListener;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.TextView.OnEditorActionListener;
import android.widget.Toast;
import android.widget.ToggleButton;

public class TrackMeActivity extends Activity{
	private static final String TAG = "ActiveTracker";
	private static final String EVENTS_URL = "http://www.len.ro/activeTracker/event.py";

	private static JSONArray events = null;

	private String getEvents(){
		StringBuilder builder = new StringBuilder();
		HttpClient client = new DefaultHttpClient();
		HttpGet httpGet = new HttpGet(EVENTS_URL);
		try {
			HttpResponse response = client.execute(httpGet);
			StatusLine statusLine = response.getStatusLine();
			int statusCode = statusLine.getStatusCode();
			if (statusCode == 200) {
				HttpEntity entity = response.getEntity();
				InputStream content = entity.getContent();
				BufferedReader reader = new BufferedReader(new InputStreamReader(content));
				String line;
				while ((line = reader.readLine()) != null) {
					builder.append(line);
				}
				return builder.toString();
			} else {
				Log.e(TAG, "Failed to get events:" + statusLine);
			}
		} catch (Exception e) {
			Log.e(TAG, e.toString());
			return null;
		}
		return null;
	}

	private void fillSpinner(){
		try {
			Spinner eventsSpinner = (Spinner) findViewById(R.id.events);
			if(events != null && events.length() > 0 && eventsSpinner.getAdapter() == null){
				List<Event> eventsList = new ArrayList<Event>();
				for (int i = 0; i < events.length(); i++) {
					JSONObject event = events.getJSONObject(i);
					if(event.has("events")){
						JSONArray categories = event.getJSONArray("events"); 
						for(int j = 0; j < categories.length(); j++){
							JSONObject category = categories.getJSONObject(j);
							eventsList.add(new Event(category));
						}
					}else{
						eventsList.add(new Event(event));
					}
				}
				ArrayAdapter<Event> dataAdapter = new ArrayAdapter<Event>(this, android.R.layout.simple_spinner_item, eventsList);
				dataAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
				eventsSpinner.setAdapter(dataAdapter);
			}
		} catch (JSONException e) {
			Log.e(TAG, e.toString());
		}
	}
	
	private boolean fillEvents(){
		try {
			//get the events
			if(events == null || (events != null && events.length() == 0)){
				Toast.makeText(getApplicationContext(), getString(R.string.statusWaitingForEvents), Toast.LENGTH_SHORT).show();
				String eventsResponse = getEvents();
				if(eventsResponse != null){
					events = new JSONArray(getEvents());
					Log.i(TAG, "Number of events: " + events.length());
					fillSpinner();
					return true;
				}else{
					Toast.makeText(getApplicationContext(), getString(R.string.noDataConnection), Toast.LENGTH_LONG).show();
				}
			}else{
				fillSpinner();
				return true;
			}
		} catch (Exception e) {
			Log.e(TAG, e.toString());
		}
		return false;
	}

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		Log.i(TAG, "onCreate");
		setContentView(R.layout.main);

		fillEvents();

		/*Spinner eventSpinner = (Spinner)findViewById(R.id.events);
		eventSpinner.setOnTouchListener(new OnTouchListener() {
			@Override
			public boolean onTouch(View v, MotionEvent event) {
				return fillEvents();
			}
		});*/
		
		EditText editText = (EditText) findViewById(R.id.trackCode);
		editText.setOnEditorActionListener(new OnEditorActionListener() {
			@Override
			public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
				boolean handled = false;
				if (actionId == EditorInfo.IME_ACTION_GO) {
					InputMethodManager imm = (InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
					imm.hideSoftInputFromWindow(v.getWindowToken(), 0);
					handled = true;
					startTracking(v);
				}
				return handled;
			}
		});

		ToggleButton trackButton = (ToggleButton)findViewById(R.id.trackButton);
		trackButton.setOnClickListener(new OnClickListener() {
			public void onClick(View v){
				ToggleButton trackButton = (ToggleButton)findViewById(R.id.trackButton);
				EditText trackCodeEditText = (EditText)findViewById(R.id.trackCode);
				Spinner eventsSpinner = (Spinner) findViewById(R.id.events);
				fillEvents();
				if(trackButton.isChecked()){
					startTracking(trackCodeEditText);
				}else{
					stopService(new Intent(TrackMeActivity.this, TrackMeService.class));
					trackCodeEditText.setEnabled(true);
					trackCodeEditText.setInputType(InputType.TYPE_CLASS_NUMBER);
					eventsSpinner.setEnabled(true);
				}
			}
		});
		
		trackButton.setOnLongClickListener(new OnLongClickListener() {
			@Override
			public boolean onLongClick(View v) {
				fillEvents();
				return true;
			}
		});

		CheckBox toggleDebug = (CheckBox)findViewById(R.id.toggleDebug);
		toggleDebug.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				boolean currentDebugState = TrackMeService.isShowDebug();
				TrackMeService.setShowDebug(!currentDebugState);
				CheckBox checkBox = (CheckBox)findViewById(R.id.toggleDebug);
				checkBox.setChecked(!currentDebugState);
			}
		});
	}

	protected void startTracking(TextView trackCodeEditText){
		ToggleButton trackButton = (ToggleButton)findViewById(R.id.trackButton);
		String trackCode = trackCodeEditText.getText().toString();
		int trackCodeInt = 0;
		try {
			trackCodeInt = Integer.parseInt(trackCode);
		} catch (NumberFormatException e) {
			trackCodeInt = 0;
		}
		Spinner eventsSpinner = (Spinner) findViewById(R.id.events);
		Event event = (Event)eventsSpinner.getSelectedItem();
		if(TextUtils.isEmpty(trackCode) || event == null || (trackCodeInt == 0 || trackCodeInt >= 1000)){
			Toast.makeText(getApplicationContext(), getString(R.string.missingData), Toast.LENGTH_SHORT).show();
			trackButton.setChecked(false);
		}else{
			trackCodeEditText.setEnabled(false);
			trackCodeEditText.setInputType(InputType.TYPE_NULL);
			eventsSpinner.setEnabled(false);
			trackButton.setChecked(true);
			TrackMeService.setTrackingData(event.getId(), trackCode);
			Intent startIntent = new Intent(TrackMeActivity.this, TrackMeService.class);
			startService(startIntent);

			//hide the activity
			Intent startMain = new Intent(Intent.ACTION_MAIN);
			startMain.addCategory(Intent.CATEGORY_HOME);
			startMain.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
			startActivity(startMain);
		}
	}

	@Override
	protected void onStart(){
		super.onStart();
		Log.i(TAG, "onStart");
		
		fillEvents();

		Integer eventId = TrackMeService.getEventId();
		String trackCode = TrackMeService.getTrackCode();
		
		Spinner eventSpinner = (Spinner)findViewById(R.id.events);
		EditText trackCodeEditText = (EditText)findViewById(R.id.trackCode);
		ToggleButton trackButton = (ToggleButton)findViewById(R.id.trackButton);
		CheckBox toggleDebug = (CheckBox)findViewById(R.id.toggleDebug);

		//re-select event
		ArrayAdapter<Event> dataAdapter = (ArrayAdapter<Event>)eventSpinner.getAdapter();
		if(eventId != null && dataAdapter != null){
			for(int i = 0; i < dataAdapter.getCount(); i++){
				Event e = dataAdapter.getItem(i);
				if(e.getId() == eventId){
					eventSpinner.setSelection(dataAdapter.getPosition(e));
				}
			}
		}
		
		//re-select trackCode
		if(!TextUtils.isEmpty(trackCode)){
			trackCodeEditText.setText(trackCode);
		}
		
		if(isTrackMeServiceRunning()){
			trackButton.setChecked(true);
			trackCodeEditText.setInputType(InputType.TYPE_NULL);
			trackCodeEditText.setEnabled(false);
		}else{
			trackButton.setChecked(false);
			trackCodeEditText.setInputType(InputType.TYPE_CLASS_NUMBER);
			trackCodeEditText.setEnabled(true);
		}
		
		toggleDebug.setChecked(TrackMeService.isShowDebug());
	}

	private boolean isTrackMeServiceRunning() {
		ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
		for (RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
			if (TrackMeService.class.getName().equals(service.service.getClassName())) {
				return true;
			}
		}
		return false;
	}

	@Override
	protected void onStop() {
		Log.i(TAG, "onStop");
		super.onStop();
	}

	final public int ABOUT = 1;

	public boolean onCreateOptionsMenu(Menu menu) {
		menu.add(0, ABOUT, 0, "About");
		return true;
	}

	public boolean onOptionsItemSelected (MenuItem item){
		switch (item.getItemId()){
		case ABOUT:
			About about = new About(this);
			about.setTitle("About");
			about.show();
			break;
		}
		return true;
	}
}