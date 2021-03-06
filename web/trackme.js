/*
ActiveTracker 
(c) 2013 len@len.ro
Version: $Id: trackme.js,v 1.35 2013/10/21 14:29:44 len Exp $
*/
var map;
var bounds = null;
var viewBounds = null;
var mapBounds = null;
var tracks = {};
var users = {};
var msgs = {};
var msgKeys = ['cp', 'lap', 'rank'];
var lastT = '';
var atEvent;
var blockCSS = { 
    border: 'none', 
    padding: '15px', 
    backgroundColor: '#000', 
    '-webkit-border-radius': '10px', 
    '-moz-border-radius': '10px', 
    opacity: .5, 
    color: '#fff' 
};
/* replay */
var replayDelta = 30;
var replayT = null;
var replayEnd = null;
var replayPlaying = false;

$(document).ready(function(){
    initUsers(eventId);
    initEvent(eventId);
});

function initUsers(eId){
    urlReq = "users.py?eventId=" + eId;
    $.ajax({type: "GET",
            url: urlReq,
            dataType: "json",
            success: function(data) {
		users = data;
	    }
	   });
}

function initEvent(eId){
    log(eId);
    urlReq = "event.py?eventId=" + eId;
    $.ajax({type: "GET",
            url: urlReq,
            dataType: "json",
            success: function(events) {
		atEvent = events[0];
		$('#eventName').text(atEvent['name']);
		if(atEvent['events'] != null){
		    var selectedEvent = atEvent['events'][0];
		    $.each(atEvent['events'], function(index) {
			var categoryId = atEvent['events'][index]['id'];
			$('#categories').append($('<option>', { 
                            value: categoryId,
                            text : atEvent['events'][index]['name']
                        }));
			if(categoryId == eventId){
			    selectedEvent = atEvent['events'][index];
			}
		    });
		    atEvent = selectedEvent;
		    $('#categories').val(atEvent['id']);
		    initT();
		}else if(atEvent['parent_fk'] != null){
		    initEvent(atEvent['parent_fk']);
		}else{
		    $('#category').hide();
		    initT();
		}
	    }
	   });
}

function printReplayTime(date){
    return int02(date.getHours()) + ':' +
	int02(date.getMinutes()) + ':' +
	int02(date.getSeconds());

}

function printDate(date){
    return date.getUTCFullYear() + '-' + 
	int02(date.getUTCMonth() + 1) + '-' +
	int02(date.getUTCDate()) + ' ' +
	int02(date.getUTCHours()) + ':' +
	int02(date.getUTCMinutes()) + ':' +
	int02(date.getUTCSeconds());
}

function parseDate(dateString){
    //2013-06-09 08:00:00+03:00
    year = parseInt(dateString.substr(0, 4), 10);
    month = parseInt(dateString.substr(5, 2), 10) - 1;
    date = parseInt(dateString.substr(8, 2), 10);
    hours = parseInt(dateString.substr(11, 2), 10); 
    minutes = parseInt(dateString.substr(14, 2), 10);
    seconds = parseInt(dateString.substr(17, 2), 10);
 
    var d = new Date(year, month, date, hours, minutes, seconds);
    d.setUTCFullYear(year);
    d.setUTCMonth(month);
    d.setUTCDate(date);
    d.setUTCHours(hours);
    d.setUTCMinutes(minutes);
    d.setUTCSeconds(seconds);
 
    return d;
}

function initT(){
    initG();

    if(replay){
	if(atEvent['start_time'] != null){
	    replayT = parseDate(atEvent['start_time']);
	    replayEnd = parseDate(atEvent['end_time']);
	    startUpdate();
	}
	return; //no date verification for replays
    }
    var now = new Date();
    var diff;

    if(atEvent['end_time'] != null){
	var endTime = parseDate(atEvent['end_time']);
        log('End time: ' + endTime);
	diff = endTime - now;
	if (diff < 0){ //event has ended
	    log('Event has ended');
	    var eventEndMsg = 'Event has ended.';
	    if(atEvent['youtube'] != null){
		eventEndMsg = eventEndMsg + '<br/><a href="' + atEvent['youtube'] + '" target="replay">Watch replay!</a>';
	    }
	    $.blockUI({ 
		css: blockCSS,
		message: eventEndMsg
	    });
	}else{
	    if(atEvent['start_time'] != null){
		var startTime = parseDate(atEvent['start_time']);
		log('Start time: ' + startTime);
		var diff = startTime - now;
		if (diff > 0){
		    log('Event will open in: ' + diff);
		    $.blockUI({ 
			css: blockCSS,
			message: 'Event will open in: <div id="countdown">' + startTime + '</div>' 
		    });
		    $('#countdown').countdown({until:startTime, onExpiry: startEvent});
		}else{
		    startUpdate();
		}
	    }
	}
    }    
}

function startEvent(){
    $.unblockUI();
    startUpdate();
}

function startUpdate(){
    updateData();
    if(replay){
	$(document).everyTime("1s", updateData);
	replayPlaying = true;
    }else{
	$(document).everyTime(atEvent['refresh_interval'] + "s", updateData); 
    }
}

function updateData(){
    urlReq = "show.py?t=" + lastT + "&eventId=" + eventId;;

    if(replay){
	urlReq = "replay.py?eventId=" + eventId + "&t=" + printDate(replayT);
	replayT.setTime(replayT.getTime() + replayDelta * 1000);
	$('#replayT').text(printReplayTime(replayT));
	if(replayEnd.getTime() <= replayT.getTime()){
	    $(document).stopTime();
	    log('Replay has ended');
	    var eventEndMsg = 'Replay has ended.';
	    $.blockUI({ 
		css: blockCSS,
		message: eventEndMsg
	    });
	}
    }

    if(!atEvent['draw_path']){
	urlReq = urlReq + "&lastOnly=t";
    }
    if(replay)
	urlReql = urlReq + "&d=" + replayDelta;
 
    $.ajax({type: "GET",
	 url: urlReq,
	 dataType: "xml",
	 success: function(xml) {
	     $(xml).find('msg').each(function(){
		 var trackCode = $(this).attr('trackCode');
		 if(!msgs.hasOwnProperty(trackCode)){
		     msgs[trackCode] = {};
		 }
		 msg = msgs[trackCode];
		 for(var m = 0; m < msgKeys.length; m++){
		     var mVal = $(this).attr(msgKeys[m]);
		     if(mVal){
			 msg[msgKeys[m]] = mVal;
		     }
		 }
	     });
	   $(xml).find('loc').each(function(){
	       var trackCode = $(this).attr('trackCode');
	       lastT = $(this).attr('t');

	       if(!tracks.hasOwnProperty(trackCode)){
		   trackData = {'lastLat': '', 'lastLon': ''};
		   if(users[trackCode] && users[trackCode]['color']){
		       trackData['color'] = users[trackCode]['color'];
		   }else{
		       trackData['color'] = randomColor();
		   }
		   if(users[trackCode] && users[trackCode]['shortname']){
		       trackData['shortCode'] = users[trackCode]['shortname']; 
		   }else{
		       trackData['shortCode'] = trackCode;
		   }
		   var polyOptions = {
		       strokeColor: '#' + trackData['color'],
		       strokeOpacity: 1.0,
		       strokeWeight: 3
		   };
		   poly = new google.maps.Polyline(polyOptions);
		   poly.setMap(map);
		   trackData['poly'] = poly;

		   //"http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + trackData['color'],
		   var pinImage = { 
		       url: "http://www.len.ro/activeTracker/pin.py?code=" + trackData['shortCode'] + "&color=" + trackData['color'],
		       size: new google.maps.Size(32, 32),
		       origin: new google.maps.Point(0,0),
		       anchor: new google.maps.Point(15, 32)
		   };
		   if(users[trackCode]){
		       if(users[trackCode]['pin']){
			   pinImage['url'] = users[trackCode]['pin'];
		       }
		   }
		   trackData['icon'] = pinImage;
		   tracks[trackCode] = trackData;
		   addStatus(trackCode);
	       }
	       trackData = tracks[trackCode];

	       var latS = $(this).attr('lat');
	       var lonS = $(this).attr('lon');
	       var updateTime = parseDate(lastT);
	       var lastUpdateLabel = createLabel(trackCode, updateTime);

	       if(latS != trackData['lastLat'] || lonS != trackData['lastLon']){
		   trackData['lastLat'] = latS;
		   trackData['lastLon'] = lonS;
		   var lat=Number(latS);
		   var lon=Number(lonS);

		   var myLatlng = new google.maps.LatLng(lat, lon);
		   var useThisPoint = true;

		   if(viewBounds){
		       if(!viewBounds.contains(myLatlng)){
			   useThisPoint = false;
			   //log('Ignored: ' + myLatlng);
		       }
		   }

		   if(useThisPoint){
		       var path = trackData['poly'].getPath();
		       
		       if(atEvent['draw_path'])
			   path.push(myLatlng);

		       if(!trackData.hasOwnProperty('marker')){
			   var marker = new google.maps.Marker({
			       position: myLatlng,
			       map: map,
			       icon: trackData['icon'],
			       title:lastUpdateLabel
			   });
			   trackData['marker'] = marker;
		       }else{
			   trackData['marker'].setPosition(myLatlng);
			   trackData['marker'].setTitle(lastUpdateLabel);
		       }
		       if($('#status-' + trackCode).length == 0)
			   addStatus(trackCode);
		       $('#status-' + trackCode).text(lastUpdateLabel);
		       bounds.extend(myLatlng);

		       if(mapBounds == null && !viewBounds){
			   map.fitBounds(bounds);
			   mapBounds = map.getBounds();
		       }
		       
		       currentBounds = map.getBounds();
		       if(mapBounds != currentBounds){
			   //log('User has changed the bounds');
		       }else{
			   //log('Fit bounds');
			   map.fitBounds(bounds);
			   mapBounds = map.getBounds();
		       }
		       //map.setCenter(myLatlng);
		   }
	       }
	   });
	 }});
}

function initG() {
    var latlng;
    if(atEvent['map_center_lat'] != null && atEvent['map_center_lon'] != null){
	latlng = new google.maps.LatLng(atEvent['map_center_lat'], atEvent['map_center_lon']);
    }else{
	latlng = new google.maps.LatLng(44.437711, 26.097367);
    }

    var mapType = google.maps.MapTypeId.ROADMAP;
    if(atEvent['map_type'] == 'ROADMAP')
	mapType = google.maps.MapTypeId.ROADMAP;
    if(atEvent['map_type'] == 'SATELLITE')
	mapType = google.maps.MapTypeId.SATELLITE;
    if(atEvent['map_type'] == 'HYBRID')
	mapType = google.maps.MapTypeId.HYBRID;
    if(atEvent['map_type'] == 'TERRAIN')
	mapType = google.maps.MapTypeId.TERRAIN;

    var myOptions = {
	zoom: 14,
	center: latlng,
	mapTypeId: mapType
    };
    map = new google.maps.Map(document.getElementById("map"), myOptions);
    var trackMeControlDiv = document.createElement('div');
    var trackMeControl = new TrackMeControl(trackMeControlDiv, map);

    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(trackMeControl);

    if(atEvent['kml_file']){
	kmlLayer = new google.maps.KmlLayer(atEvent['kml_file']);
	kmlLayer.setMap(map);
    }

    if(atEvent['view_bounds']){
	var cds = atEvent['view_bounds'].split(',');
	viewBounds = new google.maps.LatLngBounds(new google.maps.LatLng(Number(cds[0]), Number(cds[1])), new google.maps.LatLng(Number(cds[2]), Number(cds[3])));
	map.fitBounds(viewBounds);
	//log('View bounds: ' + viewBounds);
    }

    bounds = new google.maps.LatLngBounds();

    if(init){
	google.maps.event.addListenerOnce(map, 'tilesloaded', function() {
	    log('bounds: ' + map.getBounds());
	    log('update event set view_bounds = \'' + map.getBounds().getSouthWest().lat() + ',' + map.getBounds().getSouthWest().lng() + ',' + map.getBounds().getNorthEast().lat() + ',' + map.getBounds().getNorthEast().lng() + '\' where id = ' + eventId);
	});
    }

    addAutoTrack(map);
    addReplay(map);
}

function addAutoTrack(map){
    var autoTrackControlDiv = document.createElement('div');
    var autoTrackControl = new AutoTrackControl(autoTrackControlDiv, map);

    map.controls[google.maps.ControlPosition.LEFT_TOP].push(autoTrackControl);
}

function AutoTrackControl(controlDiv, map){
    var controlImg = document.createElement('div');
    controlImg.innerHTML = '<img src="auto-refresh.png" border="0" id="autoTrack" alt="Auto fit map" title="Auto fit map"/>';
    controlDiv.appendChild(controlImg);
    google.maps.event.addDomListener(controlDiv, 'click', function() {
	map.fitBounds(bounds);
	mapBounds = map.getBounds();
    });
    return controlDiv;
}

function addReplay(map){
    if(replay){
	var replayControlDiv = document.createElement('div');
	var replayControl = new ReplayControl(replayControlDiv, map);
	map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(replayControl);
    }
}

function onrStop(){
    if(replayPlaying){
	replayPlaying = false;
	$('#rStop').hide();
	$('#rPlay').show();
	$(document).stopTime();
    }
}

function onrPlay(){
    if(!replayPlaying){
	replayPlaying = true;
	$('#rPlay').hide();
	$('#rStop').show();
	$(document).everyTime("1s", updateData);
    }
}

function ReplayControl(controlDiv, map){
    var controlImg = document.createElement('div');
    controlImg.innerHTML = '<div id="replayControls"><img src="pins/stop.png" id="rStop" align="absmiddle" onclick="onrStop()" alt="Pause" title="Pause"/><img src="pins/play.png" id="rPlay" align="absmiddle" onclick="onrPlay()" style="display:none" alt="Play" title="Play"/><span id="replayT"/></div>';
    controlDiv.appendChild(controlImg);
    return controlDiv;
}

function TrackMeControl(controlDiv, map){
    var controlImg = document.createElement('div');
    //controlImg.innerHTML = '<div id="status"><a href="http://www.len.ro/activeTrackerInfo"><img src="logo.png" border="0" align="absmiddle"/>ActiveTracker</a></div>';
    statusHTML = '<button class="btn-minimize" id="toggleStatus" onclick="toggleStatus()"></button><div id="status"><iframe src="//www.facebook.com/plugins/likebox.php?href=http%3A%2F%2Fwww.facebook.com%2FActiveTrackerRo&amp;width=32&amp;height=62&amp;colorscheme=light&amp;show_faces=false&amp;header=false&amp;stream=false&amp;show_border=false" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:180px; height:62px;" allowTransparency="true"></iframe>';
    if(atEvent['msg'] != null){
	statusHTML = statusHTML + '<div id="statusMsg">' + atEvent['msg'] + '</div>';
    }
    statusHTML = statusHTML + '<div id="statusHeader">No. [Nick/Name] @ Time [CP / Lap / Rank]</div></div>';
    controlImg.innerHTML = statusHTML;
    controlDiv.appendChild(controlImg);
    return controlDiv;
}

function randomColor(){
    var h = Math.random() * 360;
    var s = 100;
    var v = 90;
    var t = tinycolor('hsv(' + h + ', ' + s + '%, ' + v + '%)')
    return t.toHex();
}

function randomColor2(){
    var r = ('0'+(Math.random()*256|0).toString(16)).slice(-2),
    g = ('0'+(Math.random()*256|0).toString(16)).slice(-2),
    b = ('0'+(Math.random()*256|0).toString(16)).slice(-2);
    var color =  '' +r+g+b;
    log('Random Color: ' + color);
    return color;
}

function int02(val){
    if(val < 10){
	return '0' + val;
    }
    return val;
}

function createLabel(trackCode, updateTime){
    var label = '#' + trackCode; 

    if(trackCode != tracks[trackCode]['shortCode']){
	label = label + " " + tracks[trackCode]['shortCode'];
    }

    if(users[trackCode]){
	label = label + '/' + users[trackCode]['label'];
    }
    label = label + ' @ ' + int02(updateTime.getHours()) + ':' + int02(updateTime.getMinutes());

    if(msgs[trackCode]){
	for(var m = 0; m < msgKeys.length; m++){
	    var msgPart = msgs[trackCode][msgKeys[m]]; 
	    if(msgPart){
		if(m == 0){
		    label = label + ' ' + msgPart;
		}else{
		    label = label + ' / ' + msgPart;
		}
	    }
	}
    }
    $('#atControl').html(label); 
    return label;
}

function log(msg){
    if (typeof console == "object") {
	console.log(msg);
    }
}

function addStatus(trackCode){
    $('#status').append($('<div class="statusLine" id="status-' + trackCode + '">Status</div>'));
    $('#status-' + trackCode).css('color', '#' + tracks[trackCode]['color']);
    $('.statusLine').sort(sortS).appendTo('#status');
}

function sortS(a, b){
    var aS = parseInt($(a).attr('id').substr(7), 10);
    var bS = parseInt($(b).attr('id').substr(7), 10);
    //D!log(aS + ", " + bS);
    return aS > bS ? 1: -1;
}

function toggleStatus(){
    $("#toggleStatus").toggleClass('btn-plus');
    $("#status").slideToggle();
}