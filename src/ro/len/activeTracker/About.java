package ro.len.activeTracker;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.text.Html;
import android.text.util.Linkify;
import android.widget.TextView;

public class About extends Dialog{
	private static final String info = "<h3>Active Tracker</h3>" +
			"Version 0.23<br/>" +
			"Copyright 2013<br/>" +
			"<b>www.len.ro</b>";
	
	private static final String legal = "Select a registered event, enter your event participation number and start tracking.<br/>" +
			"The event will be tracked on http://www.len.ro/activeTracker/. A data connection is required.<br/><br/>" +
			"<b>This App is provided \"AS IS\" without any warranty.</b>";
	
	public About(Context context) {
		super(context);
	}

	/**
	 * Standard Android on create method that gets called when the activity initialized.
	 */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		setContentView(R.layout.about);
		
		TextView tv = (TextView)findViewById(R.id.legal_text);
		tv.setText(Html.fromHtml(legal));
		tv.setLinkTextColor(Color.WHITE);
		Linkify.addLinks(tv, Linkify.ALL);
		
		tv = (TextView)findViewById(R.id.info_text);
		tv.setText(Html.fromHtml(info));
		/*tv.setLinkTextColor(Color.WHITE);
		Linkify.addLinks(tv, Linkify.ALL);*/
	}
}