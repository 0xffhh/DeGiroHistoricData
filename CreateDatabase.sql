/****** Object:  Database [Investments]    Script Date: 13/02/2021 22:52:41 ******/
CREATE DATABASE [Investments]  (EDITION = 'Basic', SERVICE_OBJECTIVE = 'Basic', MAXSIZE = 2 GB) WITH CATALOG_COLLATION = SQL_Latin1_General_CP1_CI_AS;
GO

ALTER DATABASE [Investments] SET ANSI_NULL_DEFAULT OFF 
GO

ALTER DATABASE [Investments] SET ANSI_NULLS OFF 
GO

ALTER DATABASE [Investments] SET ANSI_PADDING OFF 
GO

ALTER DATABASE [Investments] SET ANSI_WARNINGS OFF 
GO

ALTER DATABASE [Investments] SET ARITHABORT OFF 
GO

ALTER DATABASE [Investments] SET AUTO_SHRINK OFF 
GO

ALTER DATABASE [Investments] SET AUTO_UPDATE_STATISTICS ON 
GO

ALTER DATABASE [Investments] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO

ALTER DATABASE [Investments] SET CONCAT_NULL_YIELDS_NULL OFF 
GO

ALTER DATABASE [Investments] SET NUMERIC_ROUNDABORT OFF 
GO

ALTER DATABASE [Investments] SET QUOTED_IDENTIFIER OFF 
GO

ALTER DATABASE [Investments] SET RECURSIVE_TRIGGERS OFF 
GO

ALTER DATABASE [Investments] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO

ALTER DATABASE [Investments] SET ALLOW_SNAPSHOT_ISOLATION ON 
GO

ALTER DATABASE [Investments] SET PARAMETERIZATION SIMPLE 
GO

ALTER DATABASE [Investments] SET READ_COMMITTED_SNAPSHOT ON 
GO

ALTER DATABASE [Investments] SET  MULTI_USER 
GO

ALTER DATABASE [Investments] SET ENCRYPTION ON
GO

ALTER DATABASE [Investments] SET QUERY_STORE = ON
GO

ALTER DATABASE [Investments] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 7), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 10, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO

/*** The scripts of database scoped configurations in Azure should be executed inside the target database connection. ***/
GO

-- ALTER DATABASE SCOPED CONFIGURATION SET MAXDOP = 8;
GO

ALTER DATABASE [Investments] SET  READ_WRITE 
GO



/****** Object:  Table [dbo].[PortfolioLines]    Script Date: 13/02/2021 22:54:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PortfolioLines](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[portfolioId] [int] NOT NULL,
	[timestamp] [datetime2](0) NOT NULL,
	[dg_isin] [nvarchar](20) NOT NULL,
	[dg_productName] [nvarchar](50) NOT NULL,
	[dg_symbol] [nvarchar](12) NOT NULL,
	[dg_productId] [nvarchar](20) NOT NULL,
	[dg_isAdded] [bit] NOT NULL,
	[dg_positionType] [nvarchar](20) NOT NULL,
	[dg_size] [decimal](26, 6) NOT NULL,
	[dg_price] [decimal](26, 6) NOT NULL,
	[dg_productValue] [decimal](26, 6) NOT NULL,
	[dg_accruedInterest] [decimal](26, 6) NOT NULL,
	[dg_plBase] [decimal](26, 6) NOT NULL,
	[dg_todayPlBase] [decimal](26, 6) NOT NULL,
	[dg_portfolioValueCorrection] [decimal](26, 6) NOT NULL,
	[dg_breakEvenPrice] [decimal](26, 6) NOT NULL,
	[dg_averageFxRate] [decimal](26, 6) NOT NULL,
	[dg_realizedProductPl] [decimal](26, 6) NOT NULL,
	[dg_realizedFxPl] [decimal](26, 6) NOT NULL,
	[dg_todayRealizedProductPl] [decimal](26, 6) NOT NULL,
	[dg_todayRealizedFxPl] [decimal](26, 6) NOT NULL,
	[dg_contractSize] [decimal](26, 6) NOT NULL,
	[dg_productType] [nvarchar](20) NULL,
	[dg_productTypeId] [smallint] NOT NULL,
	[dg_category] [nvarchar](8) NULL,
	[dg_currency] [nvarchar](4) NOT NULL,
	[dg_exchangeId] [nvarchar](8) NOT NULL,
	[dg_onlyEodPrices] [bit] NULL,
	[dg_closePrice] [decimal](26, 6) NULL,
	[dg_closePriceDate] [date] NULL,
 CONSTRAINT [PK_PortfolioLines] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Portfolios]    Script Date: 13/02/2021 22:54:44 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Portfolios](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [varchar](255) NOT NULL,
	[description] [text] NULL,
	[dg_username] [varchar](255) NOT NULL,
 CONSTRAINT [PK_Portfolios] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UK_Username] UNIQUE NONCLUSTERED 
(
	[dg_username] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[PortfolioLines]  WITH CHECK ADD  CONSTRAINT [FK_PortfolioLines_Portfolios] FOREIGN KEY([portfolioId])
REFERENCES [dbo].[Portfolios] ([id])
GO
ALTER TABLE [dbo].[PortfolioLines] CHECK CONSTRAINT [FK_PortfolioLines_Portfolios]
GO
ALTER TABLE [dbo].[Portfolios]  WITH CHECK ADD  CONSTRAINT [FK_Portfolios_Portfolios] FOREIGN KEY([id])
REFERENCES [dbo].[Portfolios] ([id])
GO
ALTER TABLE [dbo].[Portfolios] CHECK CONSTRAINT [FK_Portfolios_Portfolios]
GO
