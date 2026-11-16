USE QuanLyQuanNet;
GO

-- Kiểm tra khóa chính
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE CONSTRAINT_NAME IN (
    SELECT CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_TYPE = 'PRIMARY KEY'
);

-- Kiểm tra khóa ngoại
SELECT
    fk.name AS TenKhoaNgoai,
    OBJECT_NAME(fk.parent_object_id) AS BangThamChieu,
    COL_NAME(fc.parent_object_id, fc.parent_column_id) AS CotThamChieu,
    OBJECT_NAME(fk.referenced_object_id) AS BangDuocThamChieu,
    COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS CotDuocThamChieu
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fc
    ON fk.object_id = fc.constraint_object_id;