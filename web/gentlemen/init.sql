insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'MTB Gentlemen Challenge', 'gentlemen', 't', 10, 'http://www.len.ro/activeTracker/gentlemen/gentlemen.kml', 'HYBRID', '2013-09-28 08:50', '2013-09-28 19:00');

update event set view_bounds = '45.41237058753685,25.128194318603505,45.573618010006705,25.527478681396474' where id = 30;