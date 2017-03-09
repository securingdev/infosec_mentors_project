-- Destroy the schema
DROP SCHEMA IF EXISTS infosecmentordb CASCADE;

-- Setup database schema:
CREATE SCHEMA IF NOT EXISTS infosecmentordb AUTHORIZATION mentor;
GRANT ALL ON SCHEMA infosecmentordb TO mentor;


ALTER DATABASE infosecmentordb OWNER TO mentor;