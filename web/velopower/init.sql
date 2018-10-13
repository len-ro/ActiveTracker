insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Velopower', 'velopower', 't', 10, 'http://www.len.ro/activeTracker/velopower/velopower.kml', 'HYBRID', '2013-09-28 09:50', '2013-09-28 17:00');

update event set view_bounds = '45.83287798728644,26.54183313720705,46.03583624566923,27.340401862792987' where id = 25;

