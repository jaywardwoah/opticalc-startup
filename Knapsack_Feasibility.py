import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
st.set_page_config(page_title="OptiFlip: Smart Reseller", layout="centered")

# --- INITIALIZE DATABASE & HISTORY ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "student": {"password": "123", "plan": "Free", "name": "Juan Dela Cruz"},
        "admin": {"password": "admin", "plan": "Premium", "name": "Engr. Jayward Balinas"}
    }

if 'history' not in st.session_state:
    st.session_state.history = []  # Stores past calculations

# Initialize Session Flags
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'payment_verified' not in st.session_state:
    st.session_state.payment_verified = False

# ==========================================
# PART 1: LOGIN & SIGN UP (WITH PAYMENT POP-UP)
# ==========================================
def login_page():
    st.title("🔐 OptiFlip Access")
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
        
        # Step 1: User Details
        new_user = st.text_input("Choose a Username")
        new_pass = st.text_input("Choose a Password", type="password")
        new_name = st.text_input("Your Full Name")
        new_plan = st.radio("Select Subscription Plan", ["Free", "Premium (₱99/mo)"], horizontal=True)
        
        # Step 2: Payment Gateway Simulation
        if "Premium" in new_plan:
            st.info("💳 **Premium Plan Selected.** Payment is required.")
            
            # The Mock "Pop-Up" Container
            with st.expander("💸 Proceed to Payment (GCash/Maya)", expanded=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    # Display a fake QR Code (Placeholder image)
                    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", caption="Scan to Pay ₱99.00")
                with c2:
                    st.write("**Payment Gateway**")
                    st.text("Merchant: OptiFlip Inc.")
                    st.text(f"Ref ID: {int(time.time())}")
                    
                    if st.button("✅ Confirm Payment"):
                        st.session_state.payment_verified = True
                        st.success("Payment Received! You can now create your account.")
        
        # Step 3: Final Create Button
        if st.button("Create Account"):
            # Validation Checks
            if new_user in st.session_state.users_db:
                st.error("Username already exists!")
            elif not new_user or not new_pass:
                st.warning("Please fill in all fields.")
            elif "Premium" in new_plan and not st.session_state.payment_verified:
                st.error("❌ Please confirm payment first!")
            else:
                # Determine Plan Name
                final_plan = "Premium" if "Premium" in new_plan else "Free"
                
                # Save to DB
                st.session_state.users_db[new_user] = {
                    "password": new_pass,
                    "plan": final_plan,
                    "name": new_name
                }
                st.success("Account Created Successfully! Go to Login Tab.")
                st.session_state.payment_verified = False # Reset for next user

# ==========================================
# PART 2: THE ALGORITHM (FIXED INT)
# ==========================================
def solve_knapsack(items, capacity):
    n = len(items)
    # FORCE INT to avoid decimal errors
    costs = [int(item['cost']) for item in items]
    profits = [int(item['profit']) for item in items]
    capacity = int(capacity)
    
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                rem_w = int(w - costs[i-1])
                dp[i][w] = max(profits[i-1] + dp[i-1][rem_w], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(items[i-1])
            w -= costs[i-1]
            w = int(w)
            
    return dp[n][capacity], selected_items

# ==========================================
# PART 3: MAIN APP INTERFACE (WITH HISTORY)
# ==========================================
def main_app():
    user = st.session_state.user_info
    plan = user['plan']
    
    # --- SIDEBAR: PROFILE & HISTORY ---
    st.sidebar.title(f"👤 {user['name']}")
    st.sidebar.caption(f"Plan: **{plan} Tier**")
    
    # HISTORY SECTION (New Feature!)
    if plan == "Premium":
        st.sidebar.divider()
        st.sidebar.subheader("📜 History Log")
        if st.session_state.history:
            for i, record in enumerate(reversed(st.session_state.history)):
                with st.sidebar.expander(f"{record['date']} - ₱{record['profit']}"):
                    st.write(f"**Budget:** ₱{record['budget']}")
                    st.write("**Items Bought:**")
                    for item in record['items']:
                        st.text(f"- {item['name']}")
        else:
            st.sidebar.caption("No saved calculations yet.")
    
    st.sidebar.divider()
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.rerun()

    # --- MAIN DASHBOARD ---
    ITEM_LIMIT = 5 if plan == "Free" else 999
    
    st.title("📈 OptiFlip Dashboard")
    
    if plan == "Free":
        st.warning("🔒 **Free Plan Active.** Upgrade to Premium for History & Unlimited Access.")

    # --- 1. MARKET SCOUTING ---
    st.divider()
    st.subheader("1. Market Scouting")
    c1, c2, c3 = st.columns(3)
    with c1: name_input = st.text_input("Item Name")
    with c2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with c3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)

    if st.button("Add Item"):
        if len(st.session_state.inventory) >= ITEM_LIMIT:
            st.error(f"🔒 Free Limit Reached ({ITEM_LIMIT} items).")
        elif name_input and cost_input > 0:
            profit = sell_input - cost_input
            st.session_state.inventory.append({
                "name": name_input, "cost": int(cost_input), 
                "sell": int(sell_input), "profit": int(profit)
            })
            st.success(f"Added {name_input}")
            time.sleep(0.5)
            st.rerun()

    if st.session_state.inventory:
        st.write("### Current Inventory List")
        df = pd.DataFrame(st.session_state.inventory)

        if plan == "Premium":
            st.caption("✨ **Pro Feature:** Edit cells directly below.")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor")
            edited_df['profit'] = edited_df['sell'] - edited_df['cost']
            st.session_state.inventory = edited_df.to_dict('records')
        else:
            st.dataframe(df, use_container_width=True)
            if st.button("Clear List"):
                st.session_state.inventory = []
                st.rerun()

    # --- 2. OPTIMIZATION ENGINE ---
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

            # --- SAVE TO HISTORY BUTTON (NEW!) ---
            if plan == "Premium":
                if st.button("💾 Save Result to History"):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    record = {
                        "date": timestamp,
                        "budget": budget,
                        "profit": max_profit,
                        "items": best_items
                    }
                    st.session_state.history.append(record)
                    st.success("Saved to History Log!")
                    time.sleep(1)
                    st.rerun()

            # --- PREMIUM TOOLS ---
            st.divider()
            st.subheader("3. Premium Tools")
            if plan == "Premium":
                st.write("📊 **Capital Allocation Chart**")
                st.bar_chart(result_df.set_index('name')['cost'])
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("📂 Download Purchase Order (CSV)", csv, "optiflip_po.csv", "text/csv")
            else:
                st.info("🔒 **Analytics, History & Export are locked.**")

# ==========================================
# EXECUTION
# ==========================================
if st.session_state.logged_in:
    main_app()
else:
    login_page()
