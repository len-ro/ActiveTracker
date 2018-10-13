package ro.len.activeTracker;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.media.MediaPlayer;
import android.os.BatteryManager;
import android.util.Log;
import android.widget.Toast;

public class BatteryMonitor extends BroadcastReceiver {

	public BatteryMonitor() {
		super();
	}

	@Override
	public void onReceive(Context context, Intent intent) { 
		int status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
		boolean isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL;

		int chargePlug = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1);
		boolean usbCharge = chargePlug == BatteryManager.BATTERY_PLUGGED_USB;
		boolean acCharge = chargePlug == BatteryManager.BATTERY_PLUGGED_AC;

		int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
		int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1);

		float batteryLevel = level / (float)scale;

		if(batteryLevel < .3f && !isCharging){
			context.stopService(new Intent(context, TrackMeService.class));
			Toast.makeText(context, R.string.statusBatteryLow, Toast.LENGTH_LONG).show();
		}    
	}
}
