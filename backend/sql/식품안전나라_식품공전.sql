SELECT * FROM pg_extension WHERE extname = 'vector';

create table public.fd_mtrl (

    id bigint generated always as identity primary key,
    name text not null
);
insert into fd_mtrl (name) values  ('원료이름' , '원료이름')
