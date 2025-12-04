-- posts 테이블에 vendor_id 컬럼 추가
ALTER TABLE posts 
ADD COLUMN vendor_id BIGINT NULL AFTER couple_id,
ADD CONSTRAINT fk_posts_vendor 
  FOREIGN KEY (vendor_id) REFERENCES vendors(id) 
  ON DELETE SET NULL;


