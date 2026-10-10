-- ============================================================
-- SmartInvoice AI — MyInvoisPortal Export
-- Database: MyInvoisPortal
-- Table: dbo.InvoiceInfo
-- Total rows: 110
-- Exported: 2026-10-11T02:12:10.693631
-- ============================================================

USE MyInvoisPortal;
GO

IF OBJECT_ID('dbo.InvoiceInfo', 'U') IS NOT NULL
    DROP TABLE dbo.InvoiceInfo;
GO

CREATE TABLE dbo.InvoiceInfo (
    InvoiceId    INT            PRIMARY KEY,
    Status       NVARCHAR(20)   NOT NULL DEFAULT 'pending',
    ErrorReason  NVARCHAR(500)  NULL,
    UUID         NVARCHAR(100)  NULL,
    QRUrl        NVARCHAR(500)  NULL,
    VerifyUrl    NVARCHAR(500)  NULL,
    SubmittedAt  DATETIME2      NULL
);
GO

INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (4, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (5, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (6, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (7, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (8, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (9, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (10, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (11, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (12, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (13, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (14, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (15, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (16, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (17, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (18, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (19, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (20, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (21, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (22, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (23, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (24, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (25, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (26, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (27, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (28, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (29, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (30, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (31, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (32, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (33, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (34, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (35, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (36, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (37, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (38, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (39, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (40, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (41, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (42, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (43, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (44, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (45, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (46, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (47, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (48, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (49, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (50, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (51, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (52, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (53, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (54, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (55, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (56, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (57, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (58, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (59, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (60, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (61, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (62, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (63, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (64, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (65, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (66, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (67, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (68, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (69, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (70, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (71, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (72, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (73, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (74, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (75, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (76, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (77, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (78, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (79, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (80, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (81, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (82, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (83, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (84, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (85, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (86, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (87, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (88, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (89, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (90, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (91, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (92, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (93, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (94, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (95, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (96, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (97, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (98, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (99, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (100, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (107, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (108, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (109, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (110, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (111, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (112, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (113, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (114, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (115, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (116, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (117, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (118, N'pending', NULL, NULL, NULL, NULL, NULL);
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES (119, N'pending', NULL, NULL, NULL, NULL, NULL);

-- Total: 110 rows imported
SELECT Status, COUNT(*) AS Count FROM dbo.InvoiceInfo GROUP BY Status;
GO