insert into event(event_index, name, code, start_time, end_time, active) values (1, 'Maratonul vinului 2013', 'marvin2013', '2013-06-09 08:00', '2013-06-09 20:00', 't');

insert into event(event_index, name, code, parent_fk, start_time, end_time, active, refresh_interval, kml_file, map_type) values (1, 'Maratonul vinului 2013 / 30km', 'marvin2013-30km', (select id from event where shortname = 'marvin2013'), '2013-06-09 08:00', '2013-06-09 20:00', 't', 15, 'http://www.len.ro/activeTracker/marvin/marvin2013-30km.kml', 'ROADMAP');

insert into event(event_index, name, code, parent_fk, start_time, end_time, active, refresh_interval, kml_file, map_type) values (1, 'Maratonul vinului 2013 / 50km', 'marvin2013-50km', (select id from event where shortname = 'marvin2013'), '2013-06-09 08:00', '2013-06-09 20:00', 't', 15, 'http://www.len.ro/activeTracker/marvin/marvin2013-50km.kml', 'ROADMAP');

insert into event(event_index, name, code, start_time, end_time, active, refresh_interval, kml_file, map_type) values (2, 'Active Test', 'active-test', '2013-06-09 08:00', '2013-06-09 20:00', 't', 15, 'active-test/active-test.kml', 'ROADMAP');

--50km id = 5
insert into event_user(event_fk, trackCode, label) values (5, '51', 'Dan Mazilu');
insert into event_user(event_fk, trackCode, label) values (5, '60', 'Len');
insert into event_user(event_fk, trackCode, label) values (5, '73', 'Ichim Sorin');
insert into event_user(event_fk, trackCode, label) values (5, '99', 'Cristian Iordan');
insert into event_user(event_fk, trackCode, label) values (5, '92', 'Doina Titei');

--30km id = 6
insert into event_user(event_fk, trackCode, label) values (6, '562', 'Paul Dragan');
insert into event_user(event_fk, trackCode, label) values (6, '418', 'Bujorescu Catalin');
insert into event_user(event_fk, trackCode, label) values (6, '427', 'Radu Sprinceana');
insert into event_user(event_fk, trackCode, label) values (6, '443', 'Cristian Tudorache');
insert into event_user(event_fk, trackCode, label) values (6, '459', 'Ioana Ghica');
insert into event_user(event_fk, trackCode, label) values (6, '475', 'Radu Ghita');
insert into event_user(event_fk, trackCode, label) values (5, '560', 'Amedeo Vancea');