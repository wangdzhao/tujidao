DROP TEMPORARY TABLE IF EXISTS dataCount;

-- 创建数量统计临时表
CREATE TEMPORARY TABLE dataCount(
	altalsCount INT,
	classCount INT,
	girlCOunt INT,
	orgCount INT,
	photoCont INT
);
-- 插入数据
INSERT INTO dataCount
(altalsCount,classCount,girlCount,orgCount,photoCont)
VALUES
(
(SELECT COUNT(*)  FROM `altals`),
(SELECT COUNT(*)  FROM `class`),
(SELECT COUNT(*)  FROM `girl` ),
(SELECT COUNT(*)  FROM `orgnation`),
(SELECT COUNT(*)  FROM `photo`));
 
-- 查看
SELECT 
altalsCount as '图集数量',  
classCount as '分类数量',
girlCOunt as '美女数量',
orgCount as '机构数量',
photoCont as '图片数量'
 
FROM dataCount;