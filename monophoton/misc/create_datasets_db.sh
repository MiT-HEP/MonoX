#!/bin/bash

DB=$1

if ! [ $DB ]
then
  DB=datasets.db
fi

echo "DROP TABLE IF EXISTS datasets;
      CREATE TABLE datasets(
        name VARCHAR(32) CONSTRAINT 'name' PRIMARY KEY ON CONFLICT ABORT,
        title VARCHAR(64),
        crosssection REAL,
        nevents INT,
        sumw REAL,
        book VARCHAR(16),
        fullname VARCHAR(128),
        comments TEXT
);" | sqlite3 $DB
