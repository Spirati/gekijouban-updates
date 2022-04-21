create table if not exists showings (
  id char(64) primary key,
  theater varchar(255),
  location varchar(255),
  added char(10) default "1969-01-01"
);