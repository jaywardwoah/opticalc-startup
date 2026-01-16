import streamlit as st
import pandas as pd
import time

# ==========================================
# CONFIGURATION & AUTHENTICATION (MOCK DB)
# ==========================================
st.set_page_config(page_title="OptiCalc: Smart Reseller", layout="centered")

# Simulating a Database of Users
# Format: "username": {"password": "password", "plan": "Free" or "Premium"}
USERS_DB = {
    "student": {"password": "123", "plan": "Free", "name": "Juan Dela Cruz"},
    "admin": {"password": "admin", "plan": "Premium", "name": "Ms. CEO"}
}

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'inventory' not in st.session_state:
    st.session_state.inventory = []

# ==========================================
# PART 1: LOGIN SCREEN
# ==========================================
def login_page():
    st.title("🔐 OptiFlip Login")
    st.markdown("Please sign in to access your reseller dashboard.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            if username in USERS_DB and USERS_DB[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_info = USERS_DB[username]
                st.success("Login Successful! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    
    st.info("💡 **Demo Credentials:**\n\n* **Free User:** `student` / `12345`\n* **Pro User:** `admin` / `admin`")

# ==========================================
# PART 2: THE ALGORITHM (KNAPSACK)
# ==========================================
def solve_knapsack(items, capacity):
    n = len(items)
    costs = [item['cost'] for item in items]
    profits = [item['profit'] for item in items]
    
    # DP Table Initialization
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # Build Table
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                dp[i][w] = max(profits[i-1] + dp[i-1][w-costs[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    # Backtracking to find selected items
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
    st.sidebar.title(f"👤 Welcome, {user['name']}")
    st.sidebar.caption(f"Subscription: **{plan} Tier**")
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()

    # Premium Logic limits
    ITEM_LIMIT = 5 if plan == "Free" else 999
    
    st.title("📈 OptiCalc Dashboard")
    
    # --- PREMIUM ADVERTISEMENT (Only for Free Users) ---
    if plan == "Free":
        st.warning("🔒 **You are on the Free Plan.** Upgrade to Premium to unlock:\n\n- ✏️ **Edit Data Directly in Table**\n- 📂 Export to Excel\n- 📊 Visual Analytics\n- ♾️ Unlimited Item Inputs")

    # --- INPUT MODULE ---
    st.divider()
    st.subheader("1. Market Scouting")
    col1, col2, col3 = st.columns(3)
    with col1: name_input = st.text_input("Item Name")
    with col2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with col3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)

    # Add Item Button
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

    # --- INVENTORY DISPLAY (THE EDITABLE PART) ---
    if st.session_state.inventory:
        st.write("### Current Inventory List")
        
        # Convert list to DataFrame for display
        df = pd.DataFrame(st.session_state.inventory)

        if plan == "Premium":
            st.caption("✨ **Pro Feature Active:** You can edit cells directly below. (Try changing a Cost!)")
            
            # THE MAGIC EDITABLE TABLE
            edited_df = st.data_editor(
                df, 
                num_rows="dynamic", # Allows adding/deleting rows
                use_container_width=True,
                key="editor"
            )
            
            # SYNC EDITS BACK TO SESSION STATE
            # Recalculate profit automatically if user changed cost/sell
            edited_df['profit'] = edited_df['sell'] - edited_df['cost']
            st.session_state.inventory = edited_df.to_dict('records')
            
        else:
            # Free users see a Static Table
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
            # Use the inventory (which might have been edited)
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

            # --- PREMIUM FEATURE: ANALYTICS & EXPORT ---
            st.divider()
            st.subheader("3. Premium Tools")
            
            if plan == "Premium":
                # Feature A: Visual Analytics
                st.write("📊 **Capital Allocation Chart**")
                st.bar_chart(result_df.set_index('name')['cost'])
                
                # Feature B: Export Data
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📂 Download Purchase Order (CSV)",
                    data=csv,
                    file_name="optiflip_purchase_order.csv",
                    mime="text/csv"
                )
            else:
                st.info("🔒 **Analytics & Export are locked.**")
                st.caption("Upgrade to Premium to visualize your data and download reports.")

# ==========================================
# MAIN EXECUTION
# ==========================================
if st.session_state.logged_in:
    main_app()
else:
    login_page()
