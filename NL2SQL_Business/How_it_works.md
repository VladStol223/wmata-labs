# How it works

Let's trace what happens when you ask: _"Who are the top 5 customers by account balance?"_

## 🎯 Step 1: Query Analysis & Intent Recognition

**What Happens:**
The agent receives your natural language question and uses AI (WatsonxChatModel) to parse the intent and identify required data elements.

**Analysis Performed:**

- **Query Type**: Top N ranking with aggregation
- **Business Objects**: customers, accounts, balance
- **Required Metric**: SUM(balance) per customer
- **Aggregation**: GROUP BY customer
- **Sorting**: ORDER BY balance DESC
- **Result Limit**: TOP 5 (LIMIT 5)

**Decision Made:**
Begin systematic schema discovery to locate customer and account balance data.

**Technical Details:**

- 2 AI reasoning calls
- Total processing time: 1.5 seconds
- Framework: LangGraph ReAct pattern (Reasoning + Acting)

---

## 🗂️ Step 2: Schema Discovery - iceberg_data Catalog

**What Happens:**
The agent queries the watsonx.data metadata to discover available schemas in the iceberg_data catalog.

**Tool Used:** `watsonxdata-list-schemas`

**Input Parameters:**

- Catalog: iceberg_data
- Engine: presto580

**Results Found:**

| Schema Name                                     | Catalog      | Description                            |
| ----------------------------------------------- | ------------ | -------------------------------------- |
| clients_schema_YourName_First3LettersOfSurname  | iceberg_data | Customer-account relationship data     |
| netezza_offload_YourName_First3LettersOfSurname | iceberg_data | Dimensional model with account details |

**Total Schemas Found:** 2

**Analysis:**

- `clients_schema_YourName_First3LettersOfSurname`: Likely contains customer-account linking tables
- `netezza_offload_YourName_First3LettersOfSurname`: Likely contains dimensional data including account balances

---

## 🤔 Step 3: Schema Selection & Planning

**What Happens:**
The agent analyzes the discovered schemas and determines which one likely contains account balance information.

**Agent Reasoning:**

- Query requires: account balance data
- Schema `netezza_offload_YourName_First3LettersOfSurname` name suggests dimensional/analytical data
- Decision: Explore `netezza_offload_YourName_First3LettersOfSurname` first for balance information

**Technical Details:**

- 2 AI reasoning calls
- Pattern matching on schema names
- No database queries executed (pure reasoning)

---

## 📚 Step 4: Table Discovery - `netezza_offload_YourName_First3LettersOfSurname

**What Happens:**
The agent lists all tables in the `netezza_offload_YourName_First3LettersOfSurname` schema to identify tables containing account data.

**Tool Used:** `watsonxdata-list-tables`

**Input Parameters:**

- Catalog: iceberg_data
- Schema: netezza_offload_YourName_First3LettersOfSurname
- Engine: presto580

**Results Found:**

| Table Name        | Type  | Estimated Rows | Purpose                             |
| ----------------- | ----- | -------------- | ----------------------------------- |
| dim_account       | TABLE | 15,000         | Account dimension with balance data |
| dim_date          | TABLE | 3,650          | Date dimension                      |
| dim_exchange      | TABLE | 50             | Exchange dimension                  |
| dim_stock         | TABLE | 5,000          | Stock dimension                     |
| fact_transactions | TABLE | 500,000        | Transaction fact table              |

**Total Tables Found:** 5

**Analysis:**

- Star schema pattern identified (dimension tables + fact table)
- `dim_account`: Account dimension - likely contains balance data ✓
- `fact_transactions`: Transaction fact table
- Other dimensions: date, exchange, stock

---

## 💡 Step 5: Identifying Data Gap

**What Happens:**
The agent recognizes that while it found account balance data, it still needs customer name information.

**Agent Reasoning:**

- Found: `dim_account` table (has balance data) ✓
- Missing: Customer names and identifiers ✗
- Hypothesis: Customer data likely in postgres_catalog.bankdemo schema
- Decision: Query postgres_catalog for customer table

**Technical Details:**

- 2 AI reasoning calls
- Cross-catalog awareness activated
- Planning multi-catalog JOIN strategy

---

## 🔍 Step 6: Table Discovery - postgres_catalog.bankdemo

**What Happens:**
The agent searches the postgres_catalog for customer-related tables.

**Tool Used:** `watsonxdata-list-tables`

**Input Parameters:**

- Catalog: postgres_catalog
- Schema: bankdemo
- Engine: presto580

**Results Found:**

| Table Name      | Type  | Estimated Rows | Description          |
| --------------- | ----- | -------------- | -------------------- |
| customers_table | TABLE | 10,000         | Customer master data |

**Total Tables Found:** 1

**Analysis:**

- Found `customers_table` in postgres_catalog.bankdemo ✓
- This table should contain customer_id and name columns
- Cross-catalog JOIN will be required (postgres_catalog + iceberg_data)

**Performance Note:**
This operation takes 11 seconds (2x longer than iceberg_data operations) due to cross-catalog metadata query overhead.

---

## 📖 Step 7: Validation Planning

**What Happens:**
The agent decides to validate the structure of dim_account before proceeding with query construction.

**Agent Reasoning:**

- Need to confirm: dim_account contains balance column
- Need to identify: Primary key for joining (likely account_id)
- Decision: Describe dim_account table structure

---

## 📋 Step 8: Table Structure Analysis - dim_account

**What Happens:**
The agent retrieves the complete column metadata for the dim_account table.

**Tool Used:** `watsonxdata-describe-table`

**Input Parameters:**

- Catalog: iceberg_data
- Schema: netezza_offload_YourName_First3LettersOfSurname
- Table: dim_account
- Engine: presto580

**Table Structure Found:**

| Column Name        | Data Type         | Nullable | Description                               |
| ------------------ | ----------------- | -------- | ----------------------------------------- |
| account_id         | integer           | No       | Primary key - Account identifier          |
| account_type       | varchar           | Yes      | Type of account (savings, checking, etc.) |
| status             | varchar           | Yes      | Account status (active, closed, etc.)     |
| opening_date       | date              | Yes      | Date account was opened                   |
| risk_level         | varchar           | Yes      | Risk assessment level                     |
| **balance**        | **decimal(18,2)** | **No**   | **Current account balance** ✓             |
| margin_enabled     | boolean           | Yes      | Whether margin trading is enabled         |
| trading_experience | varchar           | Yes      | Customer's trading experience level       |

**Total Columns:** 8  
**Primary Key:** account_id

**Key Findings:**

- ✅ `balance` column exists (decimal(18,2) - perfect for currency)
- ✅ `account_id` is the primary key (integer, not null)
- ✅ Table contains 8 columns with account attributes

---

## 🧩 Step 9: JOIN Path Analysis

**What Happens:**
The agent identifies a critical issue: there's no direct relationship between customers_table and dim_account.

**Problem Identified:**

- `customers_table` has: customer_id
- `dim_account` has: account_id
- **Missing**: Direct foreign key relationship

**Agent Reasoning:**

- Need: Bridge table to link customer_id → account_id
- Hypothesis: `accounts_table` in clients_schema_YourName_First3LettersOfSurname serves as bridge
- Decision: Describe customers_table to confirm customer_id column

---

## 📖 Step 10: Table Structure Analysis - customers_table

**What Happens:**
The agent retrieves the complete column metadata for the customers_table.

**Tool Used:** `watsonxdata-describe-table`

**Input Parameters:**

- Catalog: postgres_catalog
- Schema: bankdemo
- Table: customers_table
- Engine: presto580

**Table Structure Found:**

| Column Name     | Data Type        | Nullable | Description                             |
| --------------- | ---------------- | -------- | --------------------------------------- |
| **customer_id** | **bigint**       | **No**   | **Primary key - Customer identifier** ✓ |
| **name**        | **varchar(128)** | **No**   | **Customer full name** ✓                |
| address         | varchar(128)     | Yes      | Customer street address                 |
| zip_code        | varchar(100)     | Yes      | Postal code                             |
| credit_rating   | bigint           | Yes      | Credit score/rating                     |
| age             | bigint           | Yes      | Customer age                            |
| gender          | varchar(50)      | Yes      | Customer gender                         |
| marital_status  | varchar(50)      | Yes      | Marital status                          |
| profession      | varchar(100)     | Yes      | Customer profession                     |
| nbr_years_cli   | integer          | Yes      | Number of years as client               |
| risk_score      | real             | Yes      | Risk assessment score                   |
| state           | varchar(100)     | Yes      | State/province                          |
| city            | varchar(100)     | Yes      | City                                    |
| profile_url     | varchar(500)     | Yes      | Customer profile URL                    |
| ssn             | varchar(20)      | Yes      | Social security number                  |
| phone_number    | varchar(30)      | Yes      | Contact phone number                    |
| email           | varchar(50)      | Yes      | Email address                           |

**Total Columns:** 17  
**Primary Key:** customer_id

**Key Findings:**

- ✅ `customer_id` column exists (bigint, not null, primary key)
- ✅ `name` column exists (varchar(128), not null)
- ✅ Table contains comprehensive customer profile data (17 columns)

**Performance Note:**
This operation takes 11 seconds due to postgres_catalog cross-catalog query overhead.

---

## 🔗 Step 11: Bridge Table Identification

**What Happens:**
The agent confirms the need for a bridge table and identifies the likely candidate.

**Agent Reasoning:**

- Confirmed: customers_table has customer_id (bigint)
- Confirmed: dim_account has account_id (integer)
- Required: Bridge table with both customer_id and account_id
- Hypothesis: `accounts_table` in clients_schema_YourName_First3LettersOfSurname
- Decision: Describe accounts_table to validate

---

## 🌉 Step 12: Bridge Table Validation - accounts_table

**What Happens:**
The agent retrieves the structure of the accounts_table to confirm it can serve as a bridge.

**Tool Used:** `watsonxdata-describe-table`

**Input Parameters:**

- Catalog: iceberg_data
- Schema: clients_schema_YourName_First3LettersOfSurname
- Table: accounts_table
- Engine: presto580

**Table Structure Found:**

| Column Name     | Data Type   | Nullable | Description                    |
| --------------- | ----------- | -------- | ------------------------------ |
| **customer_id** | **integer** | **No**   | **Links to customers_table** ✓ |
| **account_id**  | **integer** | **No**   | **Links to dim_account** ✓     |

**Total Columns:** 2  
**Primary Key:** customer_id + account_id (composite)

**Key Findings:**

- ✅ Perfect bridge table structure
- ✅ Contains customer_id (links to customers_table)
- ✅ Contains account_id (links to dim_account)
- ✅ Composite primary key ensures unique customer-account relationships

**JOIN Path Confirmed:**

```txt
customers_table (customer_id)
    → accounts_table (customer_id, account_id)
        → dim_account (account_id, balance)
```

---

## 🎯 Step 13: SQL Query Construction

**What Happens:**
With all necessary metadata collected, the agent constructs the final SQL query.

**Query Requirements:**

1. Join three tables across two catalogs
2. Aggregate balance by customer
3. Sort by total balance descending
4. Limit to top 5 results

**SQL Query Generated:**

```sql
SELECT
    c.customer_id,
    c.name,
    SUM(da.balance) as total_balance
FROM postgres_catalog.bankdemo.customers_table c
JOIN iceberg_data.clients_schema_YourName_First3LettersOfSurname.accounts_table a
    ON c.customer_id = a.customer_id
JOIN iceberg_data.netezza_offload_YourName_First3LettersOfSurname.dim_account da
    ON a.account_id = da.account_id
GROUP BY c.customer_id, c.name
ORDER BY total_balance DESC
LIMIT 5
```

**Query Explanation:**

| Query Component                  | Purpose                                     |
| -------------------------------- | ------------------------------------------- |
| **SELECT** c.customer_id, c.name | Get customer ID and name                    |
| **SELECT** SUM(da.balance)       | Calculate total balance across all accounts |
| **FROM** customers_table         | Start with customer data                    |
| **JOIN** accounts_table          | Link customers to their accounts            |
| **JOIN** dim_account             | Get account balance information             |
| **GROUP BY** customer_id, name   | Aggregate balances per customer             |
| **ORDER BY** total_balance DESC  | Sort from highest to lowest balance         |
| **LIMIT** 5                      | Return only top 5 customers                 |

**Technical Details:**

- Cross-catalog JOIN (postgres_catalog + iceberg_data)
- 2 AI calls for query construction and validation
- Query follows SQL best practices (explicit table aliases, qualified column names)

---

## ✅ Step 14: Response Preparation

**What Happens:**
The agent prepares the final response with the constructed query and execution plan.

**Response Includes:**

- SQL query ready for execution
- Explanation of the query logic
- Expected result format
- Execution metadata

---

## 🎉 Step 15: Query Execution & Result Presentation

**What Happens:**
The agent executes the constructed SQL query against watsonx.data using the Presto engine, retrieves the results, and formats them for presentation to the user.

**Tool Used:** `watsonxdata-execute-select`

**Input Parameters:**

- SQL: The complete SELECT query from Step 13
- Catalog: postgres_catalog (primary catalog)
- Schema: bankdemo (default schema)
- Engine: presto580

**Execution Process:**

1. **Query Submission**: The SQL query is submitted to the Presto engine
2. **Cross-Catalog Execution**: Presto executes the query across postgres_catalog and iceberg_data
3. **JOIN Processing**: Three tables are joined and aggregated
4. **Result Retrieval**: Top 5 rows are returned
5. **Data Formatting**: Results are formatted into a readable table
6. **Generate insights**: If the appropiate rules have been added, the agent also creates insights and suggests follow-up questions

---

Back to [NL2SQL Business User Guide](README.md)

---
