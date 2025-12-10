-- 添加 cover_image_url 字段到 articles 表（如果不存在）
ALTER TABLE `articles` 
ADD COLUMN `cover_image_url` VARCHAR(500) NOT NULL DEFAULT '' 
AFTER `cover_image`;

