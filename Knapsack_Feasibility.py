import streamlit as st
import pandas as pd
import time

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
st.set_page_config(page_title="OptiCalc: Smart Reseller", layout="centered")

# --- INITIALIZE DATABASE IN SESSION STATE ---
# This allows us to add new users while the app is running!
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "student": {"password": "123", "plan": "Free", "name": "Juan Dela Cruz"},
        "admin": {"password": "admin", "plan": "Premium", "name": "Admin"}
    }

# Initialize Session Flags
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'inventory' not in st.session_state:
    st.session_state.inventory = []

# ==========================================
# PART 1: LOGIN & SIGN UP SYSTEM
# ==========================================
def login_page():
    st.title("🔐 OptiCalc Login")
    
    # Create Tabs for Login and Sign Up
    tab1, tab2 = st.tabs(["Log In", "Create Account"])
    
    # --- TAB 1: LOGIN ---
    with tab1:
        st.subheader("Welcome Back")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")
            
            if submit:
                db = st.session_state.users_db
                if username in db and db[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_info = db[username]
                    st.success("Login Successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
        
        st.caption("Try Demo: `admin` / `admin`")

    # --- TAB 2: SIGN UP ---
    with tab2:
        st.subheader("New Reseller Registration")
        with st.form("signup_form"):
            new_user = st.text_input("Choose a Username")
            new_pass = st.text_input("Choose a Password", type="password")
            new_name = st.text_input("Your Full Name")
            # For demo purposes, we let them choose the plan
            new_plan = st.selectbox("Select Subscription Plan", ["Free", "Premium"])
            
            signup_submit = st.form_submit_button("Sign Up")
            
            if signup_submit:
                if new_user in st.session_state.users_db:
                    st.error("Username already exists!")
                elif new_user and new_pass:
                    # Save new user to the session database
                    st.session_state.users_db[new_user] = {
                        "password": new_pass,
                        "plan": new_plan,
                        "name": new_name
                    }
                    st.success("Account Created! You can now Log In.")
                else:
                    st.warning("Please fill in all fields.")

# ==========================================
# PART 2: THE ALGORITHM (KNAPSACK)
# ==========================================
def solve_knapsack(items, capacity):
    n = len(items)
    costs = [item['cost'] for item in items]
    profits = [item['profit'] for item in items]
    
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                dp[i][w] = max(profits[i-1] + dp[i-1][w-costs[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(items[i-1])
            w -= costs[i-1]
            
    return dp[n][capacity], selected_items

# ==========================================
# PART 3: MAIN APP INTERFACE
# ==========================================
def main_app():
    user = st.session_state.user_info
    plan = user['plan']
    
    # --- HEADER & SIDEBAR ---
    st.sidebar.title(f"👤 {user['name']}")
    st.sidebar.caption(f"Plan: **{plan} Tier**")
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()

    ITEM_LIMIT = 5 if plan == "Free" else 999
    
    st.title("📈 OptiCalc Dashboard")
    
    if plan == "Free":
        st.warning("🔒 **Free Plan Limits Active.** Upgrade to Premium for Unlimited Access.")

    # --- INPUT MODULE ---
    st.divider()
    st.subheader("1. Market Scouting")
    col1, col2, col3 = st.columns(3)
    with col1: name_input = st.text_input("Item Name")
    with col2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with col3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)

    if st.button("Add Item"):
        if len(st.session_state.inventory) >= ITEM_LIMIT:
            st.error(f"🔒 Free Limit Reached ({ITEM_LIMIT} items). Upgrade to Add More.")
        elif name_input and cost_input > 0:
            profit = sell_input - cost_input
            st.session_state.inventory.append({
                "name": name_input, 
                "cost": int(cost_input), 
                "sell": int(sell_input), 
                "profit": int(profit)
            })
            st.success(f"Added {name_input}")
            time.sleep(0.5) 
            st.rerun()

    # --- INVENTORY DISPLAY ---
    if st.session_state.inventory:
        st.write("### Current Inventory List")
        df = pd.DataFrame(st.session_state.inventory)

        if plan == "Premium":
            st.caption("✨ **Pro Feature:** Edit cells directly below.")
            edited_df = st.data_editor(
                df, 
                num_rows="dynamic",
                use_container_width=True,
                key="editor"
            )
            # Sync edits
            edited_df['profit'] = edited_df['sell'] - edited_df['cost']
            st.session_state.inventory = edited_df.to_dict('records')
        else:
            st.dataframe(df, use_container_width=True)
            if st.button("Clear List"):
                st.session_state.inventory = []
                st.rerun()

    # --- OPTIMIZATION MODULE ---
    st.divider()
    st.subheader("2. Optimization Engine")
    budget = st.number_input("Total Capital (₱)", min_value=0, value=10000, step=500)

    if st.button("🚀 Run Analysis", type="primary"):
        if not st.session_state.inventory:
            st.warning("List is empty.")
        else:
            max_profit, best_items = solve_knapsack(st.session_state.inventory, int(budget))
            total_cost = sum(i['cost'] for i in best_items)
            roi = (max_profit / total_cost * 100) if total_cost > 0 else 0

            st.success("Analysis Complete!")
            m1, m2, m3 = st.columns(3)
            m1.metric("Investment", f"₱{total_cost:,.0f}")
            m2.metric("Profit", f"₱{max_profit:,.0f}")
            m3.metric("ROI", f"{roi:.1f}%")

            result_df = pd.DataFrame(best_items)
            st.dataframe(result_df, use_container_width=True)

            # --- PREMIUM TOOLS ---
            st.divider()
            st.subheader("3. Premium Tools")
            
            if plan == "Premium":
                st.write("📊 **Capital Allocation Chart**")
                st.bar_chart(result_df.set_index('name')['cost'])
                
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📂 Download Purchase Order (CSV)",
                    data=csv,
                    file_name="optiflip_purchase_order.csv",
                    mime="text/csv"
                )
            else:
                st.info("🔒 **Analytics & Export are locked.**")

# ==========================================
# MAIN EXECUTION
# ==========================================
if st.session_state.logged_in:
    main_app()
else:
    login_page()


