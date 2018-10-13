insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Tusnad MTB/Hobby 25km', 'tusnadMTB25', 't', 10, 'http://www.len.ro/activeTracker/tusnad-mtb/tusnad-hobby-25.kml', 'HYBRID', '2013-09-15 11:00', '2013-09-15 16:00');

insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Tusnad MTB/Race 42km', 'tusnadMTB42', 't', 10, 'http://www.len.ro/activeTracker/tusnad-mtb/tusnad-race-42.kml', 'HYBRID', '2013-09-15 10:50', '2013-09-15 16:00');

insert into event(event_index, name, code, active, refresh_interval, kml_file, map_type, start_time, end_time) values (1, 'Tusnad MTB/Maraton 57km', 'tusnadMTB57', 't', 10, 'http://www.len.ro/activeTracker/tusnad-mtb/tusnad-maraton-57.kml', 'HYBRID', '2013-09-15 10:50', '2013-09-15 16:00');

update event set view_bounds = '46.10475326852807,25.706497818603566,46.181348897334054,26.105782181396535' where id = 22;
update event set view_bounds = '46.077107661929475,25.530453637207074,46.230269209494935,26.329022362793012' where id = 23;
update event set view_bounds = '44.42784341989223,26.047456454650842,44.447576914009346,26.147277545349084' where id = 24;