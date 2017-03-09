-- Close any open connections to the database
SELECT pg_terminate_backend(pid) from pg_stat_activity where datname='infosecmentordb';

-- Drop the database (schema and tables),
-- Create the initial user, set their password:
DROP DATABASE IF EXISTS infosecmentordb;
DROP USER IF EXISTS mentor;
CREATE USER mentor WITH PASSWORD 'mentor';

-- Create the database:
CREATE DATABASE infosecmentordb WITH OWNER mentor;
GRANT ALL PRIVILEGES ON DATABASE "infosecmentordb" TO mentor;
