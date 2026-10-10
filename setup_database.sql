-- ============================================================
-- SmartInvoice AI — Database Setup Script
-- Run this in SQL Server Management Studio (SSMS) or sqlcmd
-- Creates both databases, tables, and inserts 10 sample invoices
-- ============================================================

-- ============================================================
-- Database 1: CompanyInvoiceDB — invoice data
-- ============================================================
IF DB_ID('CompanyInvoiceDB') IS NULL
    CREATE DATABASE CompanyInvoiceDB;
GO
USE CompanyInvoiceDB;
GO

-- Drop existing table if re-running
IF OBJECT_ID('dbo.Invoices', 'U') IS NOT NULL
    DROP TABLE dbo.Invoices;
GO

CREATE TABLE dbo.Invoices (
    InvoiceId        INT            IDENTITY(1,1) PRIMARY KEY,
    InvoiceNumber    NVARCHAR(30)   NOT NULL,
    SupplierName     NVARCHAR(100)  NOT NULL,
    SupplierTIN      NVARCHAR(20)   NOT NULL,
    SupplierAddress  NVARCHAR(200)  NULL,
    SupplierContact  NVARCHAR(100)  NULL,
    BuyerName        NVARCHAR(100)  NULL,
    BuyerTIN         NVARCHAR(20)   NULL,
    Mykad            NVARCHAR(20)   NULL,
    BuyerAddress     NVARCHAR(200)  NULL,
    BuyerContact     NVARCHAR(100)  NULL,
    InvoiceDate      DATE           NOT NULL,
    InvoiceTime      TIME           NOT NULL,
    Subtotal         DECIMAL(12,2)  NOT NULL,
    SSTAmount        DECIMAL(12,2)  NOT NULL,
    TotalPayable     DECIMAL(12,2)  NOT NULL
);
GO

-- Insert 10 sample invoices
SET IDENTITY_INSERT dbo.Invoices ON;
GO

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(4, N'INV-2026-0004', N'Kota Digital Solutions Sdn Bhd', N'C2023456702', N'12 Jalan Bukit Bintang, 55100 Kuala Lumpur', N'03-21456789 | billing@smartsolutions.my', N'Mutiara Retail Sdn Bhd', N'C3011122201', N'981022-48-0165', N'12 Jalan Merdeka, 50000 Kuala Lumpur', N'ahmad.rashid@email.com', N'2026-09-08', N'12:54:00', 5865.80, 469.26, 6335.06);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(5, N'INV-2026-0005', N'Sinar Maju Trading Sdn Bhd', N'C2012345601', N'88 Jalan Ampang, 50450 Kuala Lumpur', N'03-21601234 | sales@globaltrade.my', N'Kumar a/l Subramaniam', N'C3100000001', N'071207-52-0477', N'34 Jalan Ampang, 50450 Kuala Lumpur', N'siti.aminah@email.com', N'2026-10-02', N'13:21:00', 188.22, 15.06, 203.28);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(6, N'INV-2026-0006', N'Kota Digital Solutions Sdn Bhd', N'C2023456702', N'12 Jalan Bukit Bintang, 55100 Kuala Lumpur', N'03-21456789 | billing@smartsolutions.my', N'Tan Mei Ling', N'C3100000002', N'131125-34-0628', N'56 Jalan Bukit Bintang, 55100 Kuala Lumpur', N'lee.wei@email.com', N'2026-09-23', N'14:25:00', 2449.25, 195.94, 2645.19);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(7, N'INV-2026-0007', N'Cahaya Timur Consulting', N'C1234567890', N'78 Jalan Raja Laut, 50350 Kuala Lumpur', N'03-26981234 | admin@uniquetraders.my', N'Nurul Aina binti Hassan', N'C3100000003', N'740216-37-0948', N'78 Jalan Sultan, 50000 Kuala Lumpur', N'raj.kumar@email.com', N'2026-09-22', N'09:31:00', 6087.30, 486.98, 6574.28);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(8, N'INV-2026-0008', N'Pelangi Print & Pack Sdn Bhd', N'C2056789005', N'45 Jalan Sultan, 50000 Kuala Lumpur', N'03-20785678 | info@pioneertech.my', N'Nurul Aina binti Hassan', N'C3100000004', N'950126-11-0339', N'90 Jalan Tuanku Abdul Rahman, 50300 Kuala Lumpur', N'nurul.huda@email.com', N'2026-09-30', N'10:24:00', 2831.79, 226.54, 3058.33);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(9, N'INV-2026-0009', N'Cahaya Timur Consulting', N'C2067890106', N'23 Jalan Masjid India, 50100 Kuala Lumpur', N'03-26903456 | contact@innovatehub.my', N'Wong Jia Hao', N'C3100000005', N'910819-07-0998', N'11 Jalan Imbi, 55100 Kuala Lumpur', N'tan.ming@email.com', N'2026-09-24', N'14:12:00', 2990.77, 239.26, 3230.03);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(10, N'INV-2026-0010', N'Harimau Logistics Sdn Bhd', N'C2045678904', N'67 Jalan Tuanku Abdul Rahman, 50300 Kuala Lumpur', N'03-26124567 | sales@nexussupply.my', N'Tan Mei Ling', N'C3100000006', N'710725-38-0214', N'22 Jalan Raja Laut, 50350 Kuala Lumpur', N'farah.zahir@email.com', N'2026-10-08', N'17:27:00', 934.25, 74.74, 1008.99);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(11, N'INV-2026-0011', N'Harimau Logistics Sdn Bhd', N'C2045678904', N'67 Jalan Tuanku Abdul Rahman, 50300 Kuala Lumpur', N'03-26124567 | sales@nexussupply.my', N'Tanjung Hardware Sdn Bhd', N'C3022233302', N'990615-32-0404', N'33 Jalan Masjid India, 50100 Kuala Lumpur', N'lim.choong@email.com', N'2026-10-09', N'16:22:00', 4087.68, 327.01, 4414.69);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(12, N'INV-2026-0012', N'Harimau Logistics Sdn Bhd', N'C2045678904', N'67 Jalan Tuanku Abdul Rahman, 50300 Kuala Lumpur', N'03-26124567 | sales@nexussupply.my', N'Nurul Aina binti Hassan', N'C3100000007', N'660511-15-0149', N'44 Jalan Chow Kit, 50300 Kuala Lumpur', N'aisyah.mohd@email.com', N'2026-09-27', N'17:37:00', 2516.42, 201.31, 2717.73);

INSERT INTO dbo.Invoices (InvoiceId, InvoiceNumber, SupplierName, SupplierTIN, SupplierAddress, SupplierContact, BuyerName, BuyerTIN, Mykad, BuyerAddress, BuyerContact, InvoiceDate, InvoiceTime, Subtotal, SSTAmount, TotalPayable) VALUES
(13, N'INV-2026-0013', N'Harimau Logistics Sdn Bhd', N'C2045678904', N'67 Jalan Tuanku Abdul Rahman, 50300 Kuala Lumpur', N'03-26124567 | sales@nexussupply.my', N'Nurul Aina binti Hassan', N'C3100000008', N'860407-73-0798', N'55 Jalan Pahang, 53200 Kuala Lumpur', N'weiming.tan@email.com', N'2026-09-02', N'17:49:00', 4959.44, 396.76, 5356.20);
GO

SET IDENTITY_INSERT dbo.Invoices OFF;
GO

-- ============================================================
-- Database 2: MyInvoisPortal — submission status
-- ============================================================
IF DB_ID('MyInvoisPortal') IS NULL
    CREATE DATABASE MyInvoisPortal;
GO
USE MyInvoisPortal;
GO

IF OBJECT_ID('dbo.InvoiceInfo', 'U') IS NOT NULL
    DROP TABLE dbo.InvoiceInfo;
GO

CREATE TABLE dbo.InvoiceInfo (
    InvoiceId    INT            PRIMARY KEY,       -- Matches CompanyInvoiceDB.Invoices.InvoiceId
    Status       NVARCHAR(20)   NOT NULL DEFAULT 'pending',  -- pending | submitted | failed
    ErrorReason  NVARCHAR(500)  NULL,
    UUID         NVARCHAR(100)  NULL,
    QRUrl        NVARCHAR(500)  NULL,
    VerifyUrl    NVARCHAR(500)  NULL,
    SubmittedAt  DATETIME2      NULL
);
GO

-- Insert InvoiceInfo rows for the 10 sample invoices (all pending)
INSERT INTO dbo.InvoiceInfo (InvoiceId, Status, ErrorReason, UUID, QRUrl, VerifyUrl, SubmittedAt) VALUES
(4,  N'pending', NULL, NULL, NULL, NULL, NULL),
(5,  N'pending', NULL, NULL, NULL, NULL, NULL),
(6,  N'pending', NULL, NULL, NULL, NULL, NULL),
(7,  N'pending', NULL, NULL, NULL, NULL, NULL),
(8,  N'pending', NULL, NULL, NULL, NULL, NULL),
(9,  N'pending', NULL, NULL, NULL, NULL, NULL),
(10, N'pending', NULL, NULL, NULL, NULL, NULL),
(11, N'pending', NULL, NULL, NULL, NULL, NULL),
(12, N'pending', NULL, NULL, NULL, NULL, NULL),
(13, N'pending', NULL, NULL, NULL, NULL, NULL);
GO

-- ============================================================
-- Verify
-- ============================================================
USE CompanyInvoiceDB;
SELECT COUNT(*) AS TotalInvoices FROM dbo.Invoices;

USE MyInvoisPortal;
SELECT Status, COUNT(*) AS Count FROM dbo.InvoiceInfo GROUP BY Status;
GO

PRINT 'Database setup complete!';
GO
