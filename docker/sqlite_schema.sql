-- =============================================================================
--  Ab17978 业务表 SQLite schema
--  对应 web/models.py（均为 managed=False，migrate 不建，需手动建表）
--  4 张表：sequences / promoters / operons / srna_structures
--  所有 CREATE 用 IF NOT EXISTS（幂等，容器每次启动 entrypoint 都会跑）
--  字段类型与 models.py 对齐；SQLite 宽松，CHAR 长度仅作约束提示
-- =============================================================================

CREATE TABLE IF NOT EXISTS sequences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seq_id VARCHAR(50),
    description VARCHAR(500),
    seq_length INTEGER,
    sequence TEXT,
    molecular_weight REAL,
    theoretical_pi REAL,
    instability_index REAL,
    aliphatic_index REAL,
    gravy REAL
);

CREATE TABLE IF NOT EXISTS promoters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id VARCHAR(50) NOT NULL,
    length INTEGER,
    mean_tpm_global REAL,
    mean_tpm_lck REAL,
    mean_tpm_sck REAL,
    lck1 REAL,
    lck2 REAL,
    lck3 REAL,
    sck1 REAL,
    sck2 REAL,
    sck3 REAL
);

CREATE TABLE IF NOT EXISTS operons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rockhopper_range VARCHAR(50),
    strand VARCHAR(5),
    classification VARCHAR(30),
    operon_mapper_id VARCHAR(20),
    operon_mapper_range VARCHAR(50),
    genes TEXT,
    matched_id VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS srna_structures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    sequence TEXT,
    seq_length INTEGER,
    mfe_structure TEXT,
    mfe_energy VARCHAR(20),
    diversity VARCHAR(20),
    centroid_structure TEXT,
    centroid_energy VARCHAR(20),
    mec_structure TEXT,
    mec_energy VARCHAR(20),
    frequency VARCHAR(200)
);
