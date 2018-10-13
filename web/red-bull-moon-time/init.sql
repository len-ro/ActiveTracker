insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Red Bull Moon Time Ride', 'rbMoonTime', 't', 5, 'http://www.len.ro/activeTracker/red-bull-moon-time/red-bull-moon-time.kml', 'HYBRID', '2013-10-19 18:25', '2013-10-19 20:30');

update event set view_bounds = '44.39726820845314,26.081139084472625,44.41872856244386,26.129890915527312' where id = 31;
