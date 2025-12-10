-- ========================================
-- 基于Django的个人博客系统数据库脚本
-- 数据库：MySQL 8.0
-- 创建时间：2025-11-19
-- ========================================

-- 创建数据库
DROP DATABASE IF EXISTS blog_system;
CREATE DATABASE blog_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE blog_system;

-- ========================================
-- 1. 用户表 (users)
-- ========================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(150) NOT NULL UNIQUE COMMENT '用户名',
    first_name VARCHAR(150) NOT NULL DEFAULT '' COMMENT '名',
    last_name VARCHAR(150) NOT NULL DEFAULT '' COMMENT '姓',
    phone VARCHAR(11) NOT NULL UNIQUE COMMENT '手机号',
    password VARCHAR(128) NOT NULL COMMENT '密码（Django加密存储）',
    avatar VARCHAR(255) DEFAULT '/static/images/default_avatar.jpg' COMMENT '头像路径',
    nickname VARCHAR(50) DEFAULT '' COMMENT '昵称',
    bio TEXT COMMENT '个人简介',
    email VARCHAR(100) DEFAULT '' COMMENT '邮箱',
    gender TINYINT DEFAULT 0 COMMENT '性别：0-未知，1-男，2-女',
    birthday DATE NULL COMMENT '生日',
    is_active TINYINT DEFAULT 1 COMMENT '是否激活：0-未激活，1-已激活',
    is_staff TINYINT DEFAULT 0 COMMENT '是否为管理员：0-普通用户，1-管理员',
    is_superuser TINYINT DEFAULT 0 COMMENT '是否为超级管理员',
    last_login DATETIME NULL COMMENT '最后登录时间',
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_phone (phone),
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ========================================
-- 2. 文章分类表 (categories)
-- ========================================
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    description TEXT COMMENT '分类描述',
    sort_order INT DEFAULT 0 COMMENT '排序号，数字越小越靠前',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用：0-禁用，1-启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_sort_order (sort_order),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章分类表';

-- ========================================
-- 3. 标签表 (tags)
-- ========================================
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    name VARCHAR(30) NOT NULL UNIQUE COMMENT '标签名称',
    color VARCHAR(7) DEFAULT '#007bff' COMMENT '标签颜色（十六进制）',
    use_count INT DEFAULT 0 COMMENT '使用次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_name (name),
    INDEX idx_use_count (use_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签表';

-- ========================================
-- 4. 文章表 (articles)
-- ========================================
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文章ID',
    title VARCHAR(200) NOT NULL COMMENT '文章标题',
    content LONGTEXT NOT NULL COMMENT '文章内容',
    summary TEXT COMMENT '文章摘要',
    cover_image VARCHAR(255) DEFAULT '' COMMENT '封面图片路径',
    author_id INT NOT NULL COMMENT '作者ID',
    category_id INT NOT NULL COMMENT '分类ID',
    status TINYINT DEFAULT 0 COMMENT '状态：0-草稿，1-已发布，2-已删除',
    is_top TINYINT DEFAULT 0 COMMENT '是否置顶：0-否，1-是',
    is_recommend TINYINT DEFAULT 0 COMMENT '是否推荐：0-否，1-是',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    published_at DATETIME NULL COMMENT '发布时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `cover_image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '封面图片URL或上传后的完整URL',
    
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    
    INDEX idx_author_id (author_id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at),
    INDEX idx_view_count (view_count),
    INDEX idx_is_top_published (is_top, published_at),
    INDEX idx_is_recommend (is_recommend)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章表';

-- ========================================
-- 5. 文章标签关联表 (article_tags)
-- ========================================
CREATE TABLE article_tags (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关联ID',
    article_id INT NOT NULL COMMENT '文章ID',
    tag_id INT NOT NULL COMMENT '标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    
    UNIQUE KEY uk_article_tag (article_id, tag_id),
    INDEX idx_article_id (article_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章标签关联表';

-- ========================================
-- 6. 评论表 (comments)
-- ========================================
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID',
    content TEXT NOT NULL COMMENT '评论内容',
    article_id INT NOT NULL COMMENT '文章ID',
    user_id INT NOT NULL COMMENT '评论用户ID',
    parent_id INT NULL COMMENT '父评论ID（回复功能）',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    status TINYINT DEFAULT 1 COMMENT '状态：0-已删除，1-正常，2-待审核',
    ip_address VARCHAR(45) DEFAULT '' COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';

-- ========================================
-- 7. 用户点赞记录表 (user_likes)
-- ========================================
CREATE TABLE user_likes (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '点赞记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    target_type TINYINT NOT NULL COMMENT '点赞目标类型：1-文章，2-评论',
    target_id INT NOT NULL COMMENT '目标ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY uk_user_like (user_id, target_type, target_id),
    INDEX idx_user_id (user_id),
    INDEX idx_target (target_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户点赞记录表';

-- ========================================
-- 8. 系统配置表 (system_config)
-- ========================================
CREATE TABLE system_config (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型：string,int,bool,json',
    description VARCHAR(255) DEFAULT '' COMMENT '配置描述',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_config_key (config_key),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ========================================
-- 9. 访问日志表 (access_logs)
-- ========================================
CREATE TABLE access_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT NULL COMMENT '用户ID（可为空，表示游客）',
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    request_url VARCHAR(500) NOT NULL COMMENT '请求URL',
    request_method VARCHAR(10) DEFAULT 'GET' COMMENT '请求方法',
    response_status INT DEFAULT 200 COMMENT '响应状态码',
    response_time INT DEFAULT 0 COMMENT '响应时间（毫秒）',
    referer VARCHAR(500) DEFAULT '' COMMENT '来源页面',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_ip_address (ip_address),
    INDEX idx_created_at (created_at),
    INDEX idx_request_url (request_url(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='访问日志表';

-- ========================================
-- 测试数据插入
-- ========================================

-- 插入用户测试数据
INSERT INTO users (username, first_name, last_name, phone, password, nickname, bio, email, gender, is_staff, is_superuser, last_login) VALUES
('admin', '', '', '13800138000', '123456', '系统管理员', '这是系统管理员账号，负责整个博客系统的管理和维护。', 'admin@blog.com', 1, 1, 1, NOW()),
('lifeshare01', '', '', '13800138001', '123456', '生活记录者', '热爱生活，喜欢用镜头记录生活中的美好瞬间，分享生活的点滴感悟。', 'lifeshare01@blog.com', 1, 0, 0, NOW()),
('photographer02', '', '', '13800138002', '123456', '风景摄影师', '专注于风景摄影，喜欢捕捉大自然和城市中的美丽瞬间，用镜头记录世界的美好。', 'photographer02@blog.com', 2, 0, 0, NOW()),
('traveler01', '', '', '13800138003', '123456', '旅行爱好者', '喜欢旅行和探索，在旅途中发现生活的美好，分享旅行中的见闻和感悟。', 'traveler01@blog.com', 1, 0, 0, NOW()),
('naturelover02', '', '', '13800138004', '123456', '自然爱好者', '热爱大自然，喜欢在自然中寻找宁静和美好，记录四季的变化和风景的美丽。', 'naturelover02@blog.com', 2, 0, 0, NOW());

-- 插入分类测试数据
INSERT INTO categories (name, description, sort_order) VALUES
('生活分享', '日常生活的点滴记录和感悟分享', 1),
('风景摄影', '美丽的自然风光和城市景观摄影作品', 2),
('旅行日记', '旅行途中的见闻和体验分享', 3),
('美食探索', '各地美食的探索和制作心得', 4),
('心情随笔', '生活中的感悟和思考', 5),
('城市漫步', '在城市中漫步发现的美好瞬间', 6),
('四季风景', '春夏秋冬不同季节的风景记录', 7),
('自然风光', '山川湖海等自然景观的分享', 8);

-- 插入标签测试数据
INSERT INTO tags (name, color, use_count) VALUES
('生活', '#ff6b6b', 15),
('风景', '#4ecdc4', 12),
('旅行', '#45b7d1', 10),
('摄影', '#f7b731', 8),
('美食', '#ee5a6f', 9),
('春天', '#6c5ce7', 6),
('夏天', '#00b894', 7),
('秋天', '#e17055', 8),
('冬天', '#74b9ff', 5),
('城市', '#a29bfe', 6),
('自然', '#00cec9', 7),
('海边', '#0984e3', 4),
('山景', '#55efc4', 5),
('日落', '#fd79a8', 6),
('分享', '#fdcb6e', 8);

-- 插入文章测试数据
INSERT INTO articles (title, content, summary, cover_image, author_id, category_id, status, is_top, is_recommend, view_count, like_count, comment_count, published_at) VALUES
('春日樱花盛开时', 
'<h2>樱花季的到来</h2><p>春天来了，公园里的樱花树开始绽放，粉色的花瓣在微风中轻轻摇曳，美得让人心醉。周末的午后，我带着相机来到这里，想要记录下这美好的瞬间。</p><h2>拍摄心得</h2><p>樱花的美在于它的短暂和绚烂，每一朵花都值得被认真对待。我选择了不同的角度，从仰拍到俯拍，从特写到全景，试图捕捉樱花最美的样子。</p><h2>感悟</h2><p>生活中有很多美好的事物，就像这樱花一样，需要我们用心去发现和记录。每一次按下快门，都是对美好生活的致敬。</p>', 
'春天是樱花盛开的季节，粉色的花瓣在微风中摇曳，美得让人心醉。用镜头记录下这美好的瞬间，分享春天的浪漫与美好。', 
'/static/images/cherry-blossom.jpg', 2, 2, 1, 1, 1, 1250, 45, 12, '2024-11-15 10:30:00'),

('海边日落的温柔时光', 
'<h2>黄昏时分</h2><p>傍晚时分，我来到海边，准备拍摄日落。天空渐渐染上了橙红色，海面波光粼粼，一切都显得那么宁静而美好。</p><h2>等待的过程</h2><p>等待日落是一个需要耐心的过程，但这个过程本身也是一种享受。看着天空的颜色一点点变化，从蓝色到橙色，再到深红色，每一刻都值得珍惜。</p><h2>最美的瞬间</h2><p>当太阳完全沉入海平面时，天空被染成了绚烂的紫红色，这一刻的美是无法用言语形容的。我按下快门，记录下这永恒的瞬间。</p>', 
'海边日落的温柔时光，天空被染成绚烂的橙红色，海面波光粼粼。用镜头捕捉这美好的瞬间，感受大自然的魅力。', 
'/static/images/sunset-beach.jpg', 2, 2, 1, 0, 1, 890, 32, 8, '2024-11-14 14:20:00'),

('城市夜景的璀璨', 
'<h2>夜幕降临</h2><p>当夜幕降临，城市的灯光开始亮起，整个城市变得璀璨夺目。我站在高处，俯瞰这座城市的夜景，感受着都市的繁华与活力。</p><h2>光影交错</h2><p>城市的夜景是光影的艺术，霓虹灯、车灯、建筑灯光交织在一起，形成了一幅美丽的画卷。每一盏灯都像是一颗星星，点亮了城市的夜空。</p><h2>都市生活</h2><p>生活在城市中，我们常常忙于工作和生活，很少有时间停下来欣赏这座城市的美。但当你真正静下心来，你会发现这座城市有着独特的魅力。</p>', 
'夜幕降临，城市的灯光开始亮起，整个城市变得璀璨夺目。站在高处俯瞰夜景，感受都市的繁华与活力。', 
'/static/images/city-night.jpg', 3, 6, 1, 0, 1, 756, 28, 6, '2024-11-13 16:45:00'),

('山间小径的宁静', 
'<h2>走进山林</h2><p>周末，我选择远离城市的喧嚣，走进山林，寻找一份宁静。山间的小径蜿蜒曲折，两旁是茂密的树木，偶尔还能听到鸟儿的歌声。</p><h2>自然的声音</h2><p>在这里，没有汽车的轰鸣，没有人群的嘈杂，只有大自然的声音。风吹过树叶的沙沙声，溪水流淌的潺潺声，还有远处传来的鸟鸣声。</p><h2>心灵的放松</h2><p>走在山间小径上，心情变得格外平静。所有的烦恼和压力都在这宁静的环境中慢慢消散，心灵得到了真正的放松。</p>', 
'走进山林，寻找一份宁静。山间小径蜿蜒曲折，两旁是茂密的树木，只有大自然的声音，心灵得到了真正的放松。', 
'/static/images/mountain-path.jpg', 2, 8, 1, 0, 0, 634, 21, 4, '2024-11-12 09:15:00'),

('秋日枫叶红似火', 
'<h2>秋天的色彩</h2><p>秋天是色彩最丰富的季节，尤其是枫叶，红得像火一样。我来到公园，看到满树的红叶，仿佛整个世界都被染成了红色。</p><h2>叶落知秋</h2><p>微风吹过，红叶从树上飘落，像一只只蝴蝶在空中飞舞。我捡起一片叶子，仔细观察它的纹理和颜色，感叹大自然的神奇。</p><h2>季节的轮回</h2><p>秋天是收获的季节，也是告别的季节。看着叶子一片片落下，我知道冬天即将到来，但我也知道，春天还会再来，这就是季节的轮回。</p>', 
'秋天是色彩最丰富的季节，枫叶红得像火一样。满树的红叶，微风吹过，红叶飘落，像蝴蝶在空中飞舞。', 
'/static/images/autumn-maple.jpg', 4, 7, 1, 0, 0, 423, 15, 3, '2024-11-11 20:30:00'),

('冬日雪景的纯净', 
'<h2>第一场雪</h2><p>今年的第一场雪来得特别早，清晨醒来，窗外已经是一片银装素裹的世界。我兴奋地拿起相机，想要记录下这纯净的雪景。</p><h2>雪中的世界</h2><p>雪后的世界变得格外安静，所有的声音都被雪吸收了。树枝上挂满了雪花，屋顶上覆盖着厚厚的雪，整个世界都变得纯净而美好。</p><h2>冬日的温暖</h2><p>虽然外面很冷，但看着这美丽的雪景，心里却感到温暖。冬天虽然寒冷，但它也有自己独特的美丽，需要我们用心去发现。</p>', 
'今年的第一场雪，窗外一片银装素裹。雪后的世界变得格外安静，树枝上挂满雪花，整个世界都变得纯净而美好。', 
'/static/images/winter-snow.jpg', 5, 7, 1, 0, 0, 312, 12, 2, '2024-11-10 15:20:00'),

('周末的慢生活', 
'<h2>放慢脚步</h2><p>周末，我选择放慢生活的节奏，不再匆忙地赶路，而是慢慢地享受生活的每一个瞬间。泡一杯茶，读一本书，或者只是静静地坐着，看着窗外的风景。</p><h2>生活的美好</h2><p>生活中有很多美好的事物，但往往因为我们太匆忙而错过了。慢下来，你会发现生活中处处都有美好，一杯热茶，一本好书，一个安静的午后。</p><h2>内心的平静</h2><p>慢生活不是懒惰，而是一种生活态度。在快节奏的现代生活中，我们需要偶尔放慢脚步，给自己一些时间，让内心得到平静和放松。</p>', 
'周末，放慢生活的节奏，不再匆忙赶路，而是慢慢享受生活的每一个瞬间。泡一杯茶，读一本书，感受生活的美好。', 
'/static/images/slow-life.jpg', 2, 1, 1, 0, 0, 567, 18, 5, '2024-11-09 11:40:00'),

('雨后的清新', 
'<h2>雨过天晴</h2><p>一场雨过后，空气变得格外清新，天空也变得更加湛蓝。我走出家门，呼吸着新鲜的空气，感受着雨后的美好。</p><h2>雨滴的美丽</h2><p>雨后的树叶上挂满了晶莹的雨滴，在阳光的照射下闪闪发光。我拿起相机，想要捕捉这些美丽的瞬间。</p><h2>新的开始</h2><p>雨后总是给人一种新的开始的感觉，仿佛所有的烦恼都被雨水冲刷干净了。心情也变得轻松起来，对生活充满了希望。</p>', 
'一场雨过后，空气变得格外清新，天空也更加湛蓝。雨后的树叶上挂满晶莹的雨滴，在阳光下闪闪发光，一切都显得那么美好。', 
'/static/images/after-rain.jpg', 2, 8, 1, 0, 0, 445, 25, 7, '2024-11-08 19:10:00');

-- 插入文章标签关联数据
INSERT INTO article_tags (article_id, tag_id) VALUES
-- 春日樱花盛开时
(1, 2), (1, 4), (1, 6), (1, 15),
-- 海边日落的温柔时光
(2, 2), (2, 4), (2, 12), (2, 14),
-- 城市夜景的璀璨
(3, 2), (3, 4), (3, 10), (3, 15),
-- 山间小径的宁静
(4, 2), (4, 11), (4, 13), (4, 15),
-- 秋日枫叶红似火
(5, 2), (5, 8), (5, 11), (5, 15),
-- 冬日雪景的纯净
(6, 2), (6, 9), (6, 11), (6, 15),
-- 周末的慢生活
(7, 1), (7, 15),
-- 雨后的清新
(8, 2), (8, 11), (8, 15);

-- 插入评论测试数据
INSERT INTO comments (content, article_id, user_id, parent_id, like_count, ip_address) VALUES
('樱花真的好美啊！照片拍得很有意境，我也想去看看。', 1, 4, NULL, 8, '192.168.1.100'),
('春天的樱花季总是让人心情愉悦，感谢分享这么美的照片。', 1, 5, NULL, 5, '192.168.1.101'),
('请问这是在哪里拍的？我也想去打卡。', 1, 4, NULL, 2, '192.168.1.100'),
('@reader01 这是在市中心的樱花公园，现在正是最佳观赏期，建议周末去。', 1, 2, 3, 3, '192.168.1.102'),
('海边的日落真的太美了，每次看到都会让人心情平静。', 2, 3, NULL, 6, '192.168.1.103'),
('日落时分的光线最柔和，拍出来的照片也最有感觉。', 2, 2, NULL, 4, '192.168.1.102'),
('城市的夜景真的很震撼，每一盏灯都像是一颗星星。', 3, 4, NULL, 7, '192.168.1.100'),
('我也喜欢拍城市夜景，但总是拍不出这种感觉，有什么技巧吗？', 3, 5, NULL, 3, '192.168.1.101'),
('山间的宁静真的很治愈，远离城市的喧嚣，心情都变好了。', 4, 3, NULL, 5, '192.168.1.103'),
('我也想去山里走走，呼吸一下新鲜空气。', 4, 4, NULL, 4, '192.168.1.100'),
('秋天的枫叶真的太美了，红得像火一样，让人忍不住想多拍几张。', 5, 5, NULL, 6, '192.168.1.101'),
('雪景拍得真美，纯净的白色世界让人心情都变得宁静了。', 6, 3, NULL, 3, '192.168.1.103'),
('慢生活真的很重要，在这个快节奏的时代，我们需要偶尔停下来。', 7, 4, NULL, 4, '192.168.1.100'),
('雨后的空气真的很清新，照片也拍得很美，让人感受到了生活的美好。', 8, 5, NULL, 8, '192.168.1.101'),
('我也喜欢雨后的感觉，一切都变得那么清新和美好。', 8, 3, NULL, 5, '192.168.1.103');

-- 插入用户点赞记录
INSERT INTO user_likes (user_id, target_type, target_id) VALUES
-- 文章点赞
(3, 1, 1), (4, 1, 1), (5, 1, 1),
(3, 1, 2), (4, 1, 2), (5, 1, 2),
(2, 1, 3), (4, 1, 3), (5, 1, 3),
(2, 1, 4), (3, 1, 4), (4, 1, 4),
(3, 1, 5), (4, 1, 5), (5, 1, 5),
-- 评论点赞
(2, 2, 1), (3, 2, 1), (5, 2, 1),
(2, 2, 2), (3, 2, 2), (4, 2, 2),
(2, 2, 5), (4, 2, 5), (5, 2, 5),
(2, 2, 7), (3, 2, 7), (5, 2, 7),
(2, 2, 11), (3, 2, 11), (4, 2, 11);

-- 插入系统配置数据
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('site_name', '生活分享博客', 'string', '网站名称'),
('site_description', '分享生活中的美好瞬间，记录风景、旅行和日常生活的点滴感悟', 'string', '网站描述'),
('site_keywords', '生活分享,风景摄影,旅行日记,生活记录,风景,摄影', 'string', '网站关键词'),
('articles_per_page', '10', 'int', '每页显示文章数量'),
('comments_per_page', '20', 'int', '每页显示评论数量'),
('allow_register', 'true', 'bool', '是否允许用户注册'),
('comment_need_audit', 'false', 'bool', '评论是否需要审核'),
('upload_max_size', '5242880', 'int', '文件上传最大大小（字节）'),
('allowed_image_types', 'jpg,jpeg,png,gif,webp', 'string', '允许上传的图片类型'),
('sms_api_key', 'your_sms_api_key_here', 'string', '短信服务API密钥'),
('email_host', 'smtp.gmail.com', 'string', '邮件服务器地址'),
('email_port', '587', 'int', '邮件服务器端口'),
('backup_enabled', 'true', 'bool', '是否启用数据备份'),
('cache_timeout', '3600', 'int', '缓存超时时间（秒）'),
('maintenance_mode', 'false', 'bool', '维护模式开关');

-- 插入访问日志测试数据
INSERT INTO access_logs (user_id, ip_address, user_agent, request_url, request_method, response_status, response_time, referer) VALUES
(2, '192.168.1.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '/', 'GET', 200, 245, ''),
(3, '192.168.1.103', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '/article/1/', 'GET', 200, 189, '/'),
(4, '192.168.1.100', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '/category/python/', 'GET', 200, 156, '/'),
(5, '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101', '/article/2/', 'GET', 200, 203, '/category/python/'),
(NULL, '192.168.1.200', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)', '/', 'GET', 200, 312, ''),
(4, '192.168.1.100', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '/user/profile/', 'GET', 200, 178, '/article/1/'),
(3, '192.168.1.103', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '/article/3/', 'GET', 200, 167, '/'),
(2, '192.168.1.102', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '/admin/', 'GET', 200, 134, '/'),
(5, '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101', '/search/?q=Django', 'GET', 200, 289, '/'),
(NULL, '192.168.1.201', 'Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0', '/article/1/', 'GET', 200, 356, 'https://www.google.com/');
