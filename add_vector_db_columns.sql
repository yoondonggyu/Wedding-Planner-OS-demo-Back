-- chat_memories 테이블에 Vector DB 컬럼 추가
ALTER TABLE chat_memories 
ADD COLUMN vector_db_id VARCHAR(255) NULL,
ADD COLUMN vector_db_collection VARCHAR(100) NULL;

