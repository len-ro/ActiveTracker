create sequence event_seq;

create table event(id integer primary key default nextval('event_seq'), event_index integer not null, name varchar(512) not null, code varchar(128) not null, parent_fk integer references event(id), logo varchar(512), start_time timestamp with time zone not null, end_time timestamp with time zone not null, active boolean not null default 'f', kml_file varchar(512), map_type varchar(128), map_center_lat numeric, map_center_lon numeric, refresh_interval integer, draw_path boolean not null default 'f', view_bounds varchar(512), youtube varchar(512), msg varchar(1024));

create sequence position_seq;

create table position(id integer primary key default nextval('position_seq'), event_fk integer references event(id), trackCode varchar(256) not null, lat numeric not null, lon numeric not null, alt numeric not null, accuracy numeric not null, gps_time timestamp not null, update_time timestamp with time zone not null default current_timestamp, estimated bool default 'f');

create index update_time_index on position (update_time);

create table event_phone(event_fk integer references event(id) not null, trackCode varchar(256) not null, phone_id varchar(256) not null, update_time timestamp with time zone not null default current_timestamp);

create table event_user(event_fk integer references event(id) not null, trackCode varchar(256) not null, label varchar(512) not null, color varchar(20), shortname varchar(20), pin varchar(1024), chip varchar(128));

create table event_msg(event_fk integer references event(id) not null, trackCode varchar(256) not null, external_time time with time zone, update_time timestamp with time zone not null default current_timestamp, cp varchar(20), lap integer, rank integer, msg varchar(128));