insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Comana Bike Fest', 'comanaS', 't', 10, 'http://www.len.ro/activeTracker/comana/comana-long.kml', 'HYBRID', '2013-09-28 09:20', '2013-09-28 15:00');

insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Comana Bike Fest/Echipe', 'comanaD', 't', 10, 'http://www.len.ro/activeTracker/comana/comana-short.kml', 'HYBRID', '2013-09-29 09:50', '2013-09-29 14:00');

update event set view_bounds = '44.11732403531007,25.997008909301712,44.19983608630057,26.196651090698197' where id = 28;

update event set view_bounds = '44.14402262190793,26.067509454650917,44.185274411765974,26.16733054534916' where id = 29;