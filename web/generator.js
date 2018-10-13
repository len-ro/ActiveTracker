$( document ).ready(function() {
    $( "#event" ).change(function() {
//	alert( $("#event").val() );
	var event_code = $("#event").val();
	var code_value = "";
	if(event_code!='0'){
	    code_value = '<div style="margin-top: 2px; margin-bottom: 2px; width: 550px; font-family: Arial,Helvetica,sans-serif; font-size: 9px; color: #535353; background-color: #ffffff; border: 2px solid #4d4d4f; font-style: normal; text-align: right; padding: 0px; padding-bottom: 3px !important;"><iframe src="http://www.len.ro/activeTracker/'+$("#event").val()+'" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" width="550" height="515"></iframe><br/>\n<a href="http://www.len.ro/activeTracker/'+$("#event").val()+'">Open ActiveTracker in new window.</a></div> ';
	}
	$( "#code" ).val(code_value);
	$( "#preview").html(code_value);
    });
});