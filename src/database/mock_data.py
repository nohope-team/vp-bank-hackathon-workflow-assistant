USER_FEATURE_METADATA = {
    "age": "Descriptions: Age, \nWhat/How: Age of the customer",
    "occupation": "Descriptions: Occupation / industry code, \nWhat/How: ISCO / internal mapping",
    "income_tier": "Descriptions: Income tier, \nWhat/How: Binned net monthly income",
    "marital_status": "Descriptions: Marital status, \nWhat/How: Single / married / divorced …",
    "household_size": "Descriptions: Household size / dependents, \nWhat/How: Integer",
    "preferred_language": "Descriptions: Preferred language, \nWhat/How: UI / KYC flag",
    "products": "Descriptions: Product‑holding vector, \nWhat/How: Flags for deposit, card, mortgage, investment…",
    "tenure_years": "Descriptions: Tenure with bank, \nWhat/How: Days since first product",
    "avg_balance": "Descriptions: Average balance (DDA + savings) 3 m, \nWhat/How: Mean balance",
    "cc_limit_util": "Descriptions: Credit‑card limit & utilisation, \nWhat/How: Limit and % used",
    "mortgage_outstanding": "Descriptions: Mortgage outstanding, \nWhat/How: Current principal",
    "investments_aum": "Descriptions: Investments AUM, \nWhat/How: Total assets under management",
    "monthly_salary": "Descriptions: Monthly salary credit, \nWhat/How: Median of last 6 credits",
    "top_mcc": "Descriptions: Top MCC spend category, \nWhat/How: Grocery, travel, fuel…",
    "ecom_pos_ratio": "Descriptions: E‑com / POS spend ratio, \nWhat/How: % online past 90 d",
    "overseas_share": "Descriptions: Overseas spend share, \nWhat/How: % cross‑border past 12 m",
    "avg_bill_pay_amt": "Descriptions: Average bill‑pay amount, \nWhat/How: Mean utility / telco payments",
    "cash_wd_freq": "Descriptions: Cash‑withdrawal frequency, \nWhat/How: # ATM txns / month",
    "mobile_login_freq": "Descriptions: Mobile‑app login freq. 30 d, \nWhat/How: Count",
    "days_since_push": "Descriptions: Last push‑notification open Δ, \nWhat/How: Days since last open",
    "preferred_channel": "Descriptions: Preferred channel, \nWhat/How: Mobile / web / branch",
    "offer_ctr": "Descriptions: Offer click‑through rate, \nWhat/How: Opens ÷ impressions",
    "offer_accepts": "Descriptions: Offer acceptance count 12 m, \nWhat/How: Integer",
    "offer_fatigue": "Descriptions: Offer fatigue score, \nWhat/How: Recency‑weighted sends",
    "declined_offer_cat": "Descriptions: Recent declined offer category, \nWhat/How: Loan, insurance, card…",
    "day_time": "Descriptions: Day‑of‑week / time‑of‑day, \nWhat/How: Real‑time stamp",
    "season_flag": "Descriptions: Season / holiday flag, \nWhat/How: Lunar NY, Black Friday…",
    "geo_region": "Descriptions: Current geo‑region, \nWhat/How: Province / city",
    "weather": "Descriptions: Weather condition tag, \nWhat/How: Rain / heat / AQI",
    "rt_spending_trigger": "Descriptions: Real‑time spending trigger, \nWhat/How: Large purchase just authorised",
    "clv_score": "Descriptions: Customer‑lifetime‑value score, \nWhat/How: Model output",
    "churn_risk": "Descriptions: Churn‑risk score, \nWhat/How: Model output",
    "propensity_scores": "Descriptions: Next‑product propensity scores, \nWhat/How: P(card), P(loan)…",
    "price_sensitivity": "Descriptions: Price‑sensitivity index, \nWhat/How: Elasticity estimate",
    "peer_cluster_vec": "Descriptions: Peer‑cluster latent factors, \nWhat/How: Embedding vector",
    "usage_journey": "Descriptions: Product_usage_journey, \nWhat/How: Journey of product usage since begin relationship with the bank to now",
    "user_id": "Descriptions: User_id, \nWhat/How: Id of the customer"
}

ADOPTION_LOG_METADATA = {
    "adopted": "Descriptions: Adoption flag, \nWhat it captures: Whether the customer currently holds the product",
    "tenure_days": "Descriptions: Tenure (days), \nWhat it captures: Days since product was opened",
    "recency_days": "Descriptions: Recency (days since last use), \nWhat it captures: Freshness of engagement",
    "activity_intensity": "Descriptions: Activity intensity, \nWhat it captures: Active days or txn count in past 30 d",
    "monetary_volume": "Descriptions: Monetary volume (3 m), \nWhat it captures: Total spend or balance over last 3 months",
    "utilisation_ratio": "Descriptions: Utilisation ratio, \nWhat it captures: Current balance ÷ credit limit (credit products)",
    "reward_redemption_rate": "Descriptions: Reward redemption rate, \nWhat it captures: Redeemed ÷ accrued rewards (past 3 m)",
    "risk_flag": "Descriptions: Risk flag, \nWhat it captures: Any delinquency/fraud event on this product",
    "user_id": "Descriptions: User_id, \nWhat it captures: Id of the customer",
    "product_id": "Descriptions: Product_id, \nWhat it captures: Id of the product"
}

PRODUCT_METADATA = {
    "category": "Descriptions: Product / offer category, \nWhat/How: Credit card, loan, insurance, merchant coupon",
    "tier": "Descriptions: Sub‑segment / tier, \nWhat/How: Classic, gold, platinum, youth, SME",
    "apr": "Descriptions: Interest rate / APR / fee, \nWhat/How: Numeric",
    "reward_type": "Descriptions: Reward type, \nWhat/How: Cashback, points, miles, voucher",
    "reward_value": "Descriptions: Reward value, \nWhat/How: % cashback, miles, THB amount",
    "eligibility": "Descriptions: Eligibility rules, \nWhat/How: Min income, credit‑score floor, existing‑product prerequisite",
    "tenor_months": "Descriptions: Tenor / lock‑in period, \nWhat/How: Months",
    "risk_adj_margin": "Descriptions: Risk‑adjusted margin, \nWhat/How: Expected profit per unit",
    "hist_conv_rate": "Descriptions: Historical conversion rate, \nWhat/How: Past CTR / acceptance",
    "hist_profit": "Descriptions: Historical profit per acceptance, \nWhat/How: Avg. revenue – cost",
    "budget_remaining": "Descriptions: Campaign budget remaining, \nWhat/How: Currency or units",
    "max_redemptions": "Descriptions: Max redemptions remaining, \nWhat/How: Integer",
    "offer_dates": "Descriptions: Offer start / end date, \nWhat/How: YYYY‑MM‑DD",
    "launch_recency_days": "Descriptions: Product launch recency, \nWhat/How: Days since launch",
    "compliance_tag": "Descriptions: Regulatory / compliance tag, \nWhat/How: e.g., suitable‑for‑prime only",
    "channels": "Descriptions: Channel availability, \nWhat/How: Mobile‑app, web, branch",
    "target_segments": "Descriptions: Target segmentation tags, \nWhat/How: Youth, traveller, HNWI, SME",
    "geo_applic": "Descriptions: Geographic applicability, \nWhat/How: Nationwide / region‑specific",
    "merchant_industry": "Descriptions: Merchant industry (partner offers), \nWhat/How: MCC or NAICS code",
    "cost_to_bank": "Descriptions: Offer cost to bank, \nWhat/How: Promo budget per redemption",
    "expected_utility": "Descriptions: Expected customer utility, \nWhat/How: Model‑estimated uplift score",
    "cross_sell_score": "Descriptions: Cross‑sell complement score, \nWhat/How: Compatibility with current holdings",
    "bundle_depth": "Descriptions: Bundle depth, \nWhat/How: # sub‑products included",
    "valid_window": "Descriptions: Valid‑time window in day, \nWhat/How: 08‑22 h, weekends only…",
    "popularity_trend": "Descriptions: Popularity trend, \nWhat/How: Acceptance velocity (WoW)",
    "product_id": "Descriptions: Product_id, \nWhat/How: Id of the product"
}

CATEGORY_DATA = {
    "DebitCard": {
        "name": "Debit Card",
        "description": "Linked to a checking or savings account; allows users to spend their own money directly.",
        "user_portrait": "Young to middle-aged; salary earners; uses card for daily transactions and ATM withdrawals; prefers real-time balance tracking."
    },
    "PersonalLoan": {
        "name": "Personal Loan",
        "description": "Unsecured loan for personal needs such as education, travel, or emergency expenses.",
        "user_portrait": "25–45 years old; middle-income salaried individuals; needs quick cash for specific events; has a stable repayment history."
    },
    "Overdraft": {
        "name": "Overdraft",
        "description": "Allows account holders to withdraw more than the balance available, up to a limit.",
        "user_portrait": "Small business owners or freelancers; needs short-term liquidity; irregular income patterns; moderate risk appetite."
    },
    "FXTransfer": {
        "name": "Foreign Exchange Transfer",
        "description": "Enables users to send or receive money in foreign currency; used for international payments.",
        "user_portrait": "Professionals working abroad; students studying overseas; international business clients; high digital banking usage."
    },
    "Insurance": {
        "name": "Insurance",
        "description": "Products that provide protection against risk (life, health, travel, etc.).",
        "user_portrait": "Adults with dependents; middle- to high-income users; risk-averse mindset; concerned about financial stability."
    },
    "Mortgage": {
        "name": "Mortgage",
        "description": "A long-term loan secured against property; used for home purchase or real estate investment.",
        "user_portrait": "30–55 years old; stable income; often married with family; first-time home buyers or property investors."
    },
    "CreditCard": {
        "name": "Credit Card",
        "description": "Allows users to borrow funds up to a credit limit for purchases, with repayment flexibility.",
        "user_portrait": "Urban professionals; 25–45 years old; regular income; seeks rewards, cashback, or credit building."
    },
    "InvestmentFund": {
        "name": "Investment Fund",
        "description": "Pooled investment vehicle offering diversified exposure to markets (e.g., mutual funds).",
        "user_portrait": "Financially literate users; aged 30–60; middle to high income; long-term wealth planning focus."
    },
    "FixedDeposit": {
        "name": "Fixed Deposit",
        "description": "Time-bound deposit with fixed interest; higher returns than savings accounts.",
        "user_portrait": "Risk-averse individuals; retirees or senior citizens; prefer stability over high returns; may not need short-term liquidity."
    },
    "SavingsAccount": {
        "name": "Savings Account",
        "description": "Basic banking product for storing money with modest interest and high liquidity.",
        "user_portrait": "All age groups; entry-level banking product; used for salary credit, bill payments; high transaction frequency."
    }
}

# List of special columns
ARRAY_COLUMNS = [
    "target_segments",
    "channels",
    "usage_journey",
]

VECTOR_COLUMNS = [
    "peer_cluster_vec",
]

DICTIONARY_COLUMNS = [
    "products",
    "cc_limit_util",
    "propensity_scores",
]

MAP_ORG_COL_TO_NEW_COL = {'peer_cluster_vec': ['peer_cluster_vec_0',
                                'peer_cluster_vec_1',
                                'peer_cluster_vec_2',
                                'peer_cluster_vec_3',
                                'peer_cluster_vec_4'],
                'target_segments': ['target_segments_0',
                                'target_segments_1',
                                'target_segments_2'],
                'channels': ['channels_0',
                                'channels_1',
                                'channels_2',
                                'channels_3',
                                'channels_4'],
                'usage_journey': ['usage_journey_0',
                                'usage_journey_1',
                                'usage_journey_2',
                                'usage_journey_3',
                                'usage_journey_4',
                                'usage_journey_5',
                                'usage_journey_6',
                                'usage_journey_7'],
                'products': ['products_DDA',
                                'products_SAV',
                                'products_CC',
                                'products_MORT',
                                'products_INV',
                                'products_INS',
                                'products_LOAN',
                                'products_FX'],
                'cc_limit_util': ['cc_limit_util_limit', 'cc_limit_util_utilisation'],
                'propensity_scores': ['propensity_scores_CreditCard',
                                'propensity_scores_PersonalLoan',
                                'propensity_scores_Mortgage',
                                'propensity_scores_Insurance',
                                'propensity_scores_Investment']}

IGNORE_COLUMNS = [
    "eligibility",
    "user_id",
    "product_id",
    "offer_dates",
    "day_time", 
    "risk_flag",
]