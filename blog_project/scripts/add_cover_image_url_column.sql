-- 添加 cover_image_url 字段到 articles 表
ALTER TABLE articles ADD COLUMN cover_image_url VARCHAR(500) DEFAULT '' COMMENT '封面图片URL或上传后的完整URL';

