create table food_doc (
    id bigserial primary key,
    content text,
    metadata jsonb,
    embedding vector(1024)
);
drop table food_doc;

alter table food_doc rename metadata to langchain_metadata;

alter table food_doc
alter column langchain_metadata type jsonb using langchain_metadata::jsonb;
