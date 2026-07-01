"""
SQL initialization script for AI Portfolio Analytics Dashboard
"""

-- Drop tables if they exist (for fresh start)
DROP TABLE IF EXISTS risk_metrics CASCADE;
DROP TABLE IF EXISTS payment_history CASCADE;
DROP TABLE IF EXISTS loan_accounts CASCADE;
DROP TABLE IF EXISTS customer_demographics CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS loan_officers CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS kpi_snapshots CASCADE;

-- Branches table
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    branch_name VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    manager_id INTEGER,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_branch_name UNIQUE(branch_name)
);

CREATE INDEX idx_branches_region ON branches(region);
CREATE INDEX idx_branches_manager ON branches(manager_id);

-- Loan Officers table
CREATE TABLE loan_officers (
    id SERIAL PRIMARY KEY,
    officer_name VARCHAR(255) NOT NULL,
    branch_id INTEGER NOT NULL,
    hire_date TIMESTAMP NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

CREATE INDEX idx_officers_branch ON loan_officers(branch_id);
CREATE INDEX idx_officers_region ON loan_officers(region);

-- Portfolios table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    portfolio_name VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch_id INTEGER NOT NULL,
    total_exposure NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

CREATE INDEX idx_portfolios_region ON portfolios(region);
CREATE INDEX idx_portfolios_branch ON portfolios(branch_id);

-- Customer Demographics table
CREATE TABLE customer_demographics (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    gender VARCHAR(20),
    age INTEGER,
    income_level VARCHAR(50),
    occupation VARCHAR(100),
    financial_inclusion_score NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_gender ON customer_demographics(gender);
CREATE INDEX idx_customers_income ON customer_demographics(income_level);

-- Loan Accounts table
CREATE TABLE loan_accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    account_name VARCHAR(255) NOT NULL,
    portfolio_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    officer_id INTEGER NOT NULL,
    approval_date TIMESTAMP NOT NULL,
    loan_amount NUMERIC(15, 2) NOT NULL,
    interest_rate NUMERIC(5, 4) NOT NULL,
    status VARCHAR(50) NOT NULL,
    ltv_ratio NUMERIC(5, 4),
    collateral_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (officer_id) REFERENCES loan_officers(id)
);

CREATE INDEX idx_accounts_portfolio ON loan_accounts(portfolio_id);
CREATE INDEX idx_accounts_branch ON loan_accounts(branch_id);
CREATE INDEX idx_accounts_officer ON loan_accounts(officer_id);
CREATE INDEX idx_accounts_status ON loan_accounts(status);
CREATE INDEX idx_accounts_account_number ON loan_accounts(account_number);

-- Payment History table
CREATE TABLE payment_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    amount_paid NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    days_past_due INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES loan_accounts(id) ON DELETE CASCADE
);

CREATE INDEX idx_payments_account ON payment_history(account_id);
CREATE INDEX idx_payments_date ON payment_history(payment_date);
CREATE INDEX idx_payments_status ON payment_history(status);

-- Risk Metrics table
CREATE TABLE risk_metrics (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    risk_date TIMESTAMP NOT NULL,
    par_status VARCHAR(50) NOT NULL,
    npl_flag BOOLEAN DEFAULT FALSE,
    arrears_ratio NUMERIC(5, 4),
    interest_arrear NUMERIC(15, 2),
    restructure_count INTEGER DEFAULT 0,
    risk_score NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES loan_accounts(id) ON DELETE CASCADE
);

CREATE INDEX idx_risk_account ON risk_metrics(account_id);
CREATE INDEX idx_risk_date ON risk_metrics(risk_date);
CREATE INDEX idx_risk_par_status ON risk_metrics(par_status);
CREATE INDEX idx_risk_npl_flag ON risk_metrics(npl_flag);

-- KPI Snapshots table for caching aggregated metrics
CREATE TABLE kpi_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date TIMESTAMP NOT NULL,
    metric_type VARCHAR(100) NOT NULL,
    metric_scope VARCHAR(100) NOT NULL,
    scope_id VARCHAR(100),
    metric_value NUMERIC(15, 4) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kpi_snapshots_date ON kpi_snapshots(snapshot_date);
CREATE INDEX idx_kpi_snapshots_type ON kpi_snapshots(metric_type);
CREATE INDEX idx_kpi_snapshots_scope ON kpi_snapshots(metric_scope, scope_id);

-- Views for common queries

-- PAR Summary View
CREATE OR REPLACE VIEW v_par_summary AS
SELECT 
    COUNT(DISTINCT la.id) as total_accounts,
    SUM(CASE WHEN rm.par_status = '0-30' THEN 1 ELSE 0 END) as par_30,
    SUM(CASE WHEN rm.par_status = '31-60' THEN 1 ELSE 0 END) as par_60,
    SUM(CASE WHEN rm.par_status = '61-90' THEN 1 ELSE 0 END) as par_90,
    SUM(CASE WHEN rm.par_status IN ('91-180', '180+') THEN 1 ELSE 0 END) as par_180_plus,
    SUM(CASE WHEN rm.par_status != '0-30' THEN 1 ELSE 0 END) as total_par_accounts,
    SUM(la.loan_amount) as total_portfolio,
    SUM(CASE WHEN rm.par_status != '0-30' THEN la.loan_amount ELSE 0 END) as par_amount
FROM loan_accounts la
LEFT JOIN (
    SELECT DISTINCT ON (account_id) account_id, par_status, risk_date
    FROM risk_metrics
    ORDER BY account_id, risk_date DESC
) rm ON la.id = rm.account_id;

-- NPL Summary View
CREATE OR REPLACE VIEW v_npl_summary AS
SELECT 
    COUNT(DISTINCT CASE WHEN rm.npl_flag THEN la.id END) as npl_count,
    SUM(CASE WHEN rm.npl_flag THEN la.loan_amount ELSE 0 END) as npl_amount,
    ROUND(
        COUNT(DISTINCT CASE WHEN rm.npl_flag THEN la.id END)::NUMERIC / 
        COUNT(DISTINCT la.id) * 100, 2
    ) as npl_ratio,
    SUM(CASE WHEN ph.status = 'On-time' THEN ph.amount_paid ELSE 0 END) as collections
FROM loan_accounts la
LEFT JOIN (
    SELECT DISTINCT ON (account_id) account_id, npl_flag
    FROM risk_metrics
    ORDER BY account_id, risk_date DESC
) rm ON la.id = rm.account_id
LEFT JOIN payment_history ph ON la.id = ph.account_id;

-- Branch Performance View
CREATE OR REPLACE VIEW v_branch_performance AS
SELECT 
    b.id as branch_id,
    b.branch_name,
    b.region,
    COUNT(DISTINCT la.id) as total_accounts,
    SUM(la.loan_amount) as total_exposure,
    COUNT(DISTINCT CASE WHEN la.status = 'Active' THEN la.id END) as active_accounts,
    COUNT(DISTINCT CASE WHEN la.status = 'Defaulted' THEN la.id END) as defaulted_accounts,
    ROUND(
        COUNT(DISTINCT CASE WHEN rm.npl_flag THEN la.id END)::NUMERIC / 
        COUNT(DISTINCT la.id) * 100, 2
    ) as npl_ratio
FROM branches b
LEFT JOIN loan_accounts la ON b.id = la.branch_id
LEFT JOIN (
    SELECT DISTINCT ON (account_id) account_id, npl_flag
    FROM risk_metrics
    ORDER BY account_id, risk_date DESC
) rm ON la.id = rm.account_id
GROUP BY b.id, b.branch_name, b.region;

-- Officer Performance View
CREATE OR REPLACE VIEW v_officer_performance AS
SELECT 
    lo.id as officer_id,
    lo.officer_name,
    lo.branch_id,
    b.branch_name,
    COUNT(DISTINCT la.id) as total_accounts,
    SUM(la.loan_amount) as total_exposure,
    SUM(ph.amount_paid) as collections,
    COUNT(DISTINCT CASE WHEN la.status = 'Defaulted' THEN la.id END) as defaulted_accounts
FROM loan_officers lo
LEFT JOIN branches b ON lo.branch_id = b.id
LEFT JOIN loan_accounts la ON lo.id = la.officer_id
LEFT JOIN payment_history ph ON la.id = ph.account_id
GROUP BY lo.id, lo.officer_name, lo.branch_id, b.branch_name;

COMMIT;
