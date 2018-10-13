insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Rocket Bike', 'rocketBike', 't', 10, 'http://www.len.ro/activeTracker/rocket-bike/rocket-bike.kml', 'HYBRID', '2013-09-21 09:20', '2013-09-21 17:00');

update event set view_bounds = '44.41531296604524,26.236924454650875,44.459131491865946,26.336745545349117' where id = 26;

