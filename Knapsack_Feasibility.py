import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ==========================================
# CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="OptiFlip: Smart Reseller", layout="centered")

# --- DATABASE (MOCK) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "admin", "plan": "Premium", "name": "Engr. Jayward Balinas"}
    }

# --- SESSION FLAGS ---
# Default user is "Guest" (Free)
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "Guest User", "plan": "Free"}
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_paywall' not in st.session_state:
    st.session_state.show_paywall = False # Controls the Pop-up
if 'payment_verified' not in st.session_state:
    st.session_state.payment_verified = False

# ==========================================
# PART 1: THE "GRAMMARLY" PAYWALL SCREEN
# ==========================================
def paywall_screen():
    st.title("🚀 Unlock OptiFlip Premium")
    st.markdown("You hit a Pro feature! Log in or Upgrade to continue.")
    
    # Close Button (Go back to Free version)
    if st.button("← Back to Free Version"):
        st.session_state.show_paywall = False
        st.rerun()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Log In (Existing User)", "Upgrade Now (Sign Up)"])
    
    # --- TAB 1: LOGIN ---
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                db = st.session_state.users_db
                if username in db and db[username]["password"] == password:
                    st.session_state.user_info = db[username]
                    st.session_state.show_paywall = False # Close Paywall
                    st.success(f"Welcome back, {db[username]['name']}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

    # --- TAB 2: SIGN UP + PAYMENT ---
    with tab2:
        st.write("### ⚡ Create Premium Account")
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        new_name = st.text_input("Your Name")
        
        # Payment Gateway Simulation
        st.info("💳 **Premium Plan: ₱99/month**")
        with st.expander("💸 Proceed to Payment (GCash/Maya)", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", caption="Scan to Pay")
            with c2:
                st.write("**Payment Gateway**")
                if st.button("✅ Confirm Payment"):
                    st.session_state.payment_verified = True
                    st.success("Payment Received!")

        if st.button("Complete Registration"):
            if not st.session_state.payment_verified:
                st.error("❌ Please confirm payment first!")
            elif new_user and new_pass:
                # Create Account
                st.session_state.users_db[new_user] = {
                    "password": new_pass, "plan": "Premium", "name": new_name
                }
                # Auto-Login the new user
                st.session_state.user_info = st.session_state.users_db[new_user]
                st.session_state.show_paywall = False
                st.success("Welcome to Premium!")
                st.session_state.payment_verified = False
                time.sleep(1)
                st.rerun()

# ==========================================
# PART 2: THE ALGORITHM (Standard)
# ==========================================
def solve_knapsack(items, capacity):
    # FORCE INT
    costs = [int(item['cost']) for item in items]
    profits = [int(item['profit']) for item in items]
    capacity = int(capacity)
    n = len(items)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                dp[i][w] = max(profits[i-1] + dp[i-1][int(w-costs[i-1])], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(items[i-1])
            w -= costs[i-1]
            w = int(w)
    return dp[n][capacity], selected

# ==========================================
# PART 3: MAIN APP (THE TRIGGER SYSTEM)
# ==========================================
def main_app():
    user = st.session_state.user_info
    plan = user['plan']
    is_premium = plan == "Premium"
    
    # --- HEADER ---
    c1, c2 = st.columns([3, 1])
    with c1: st.title("📈 OptiFlip Dashboard")
    with c2: 
        if is_premium:
            st.success(f"👑 {user['name']}")
            if st.button("Log Out"):
                st.session_state.user_info = {"name": "Guest User", "plan": "Free"}
                st.rerun()
        else:
            if st.button("🔓 Login / Upgrade"):
                st.session_state.show_paywall = True
                st.rerun()

    # --- 1. MARKET SCOUTING ---
    st.divider()
    st.subheader("1. Market Scouting")
    
    c1, c2, c3 = st.columns(3)
    with c1: name_input = st.text_input("Item Name")
    with c2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with c3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)

    # TRIGGER 1: ADDING TOO MANY ITEMS
    if st.button("Add Item"):
        if not is_premium and len(st.session_state.inventory) >= 5:
            # TRIGGER THE PAYWALL
            st.session_state.show_paywall = True
            st.rerun()
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
        df = pd.DataFrame(st.session_state.inventory)
        
        # TRIGGER 2: EDITABLE TABLE
        if is_premium:
            st.caption("✨ **Pro Mode:** Edit cells directly.")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor")
            edited_df['profit'] = edited_df['sell'] - edited_df['cost']
            st.session_state.inventory = edited_df.to_dict('records')
        else:
            st.dataframe(df, use_container_width=True)
            # Fake "Unlock" button to tempt them
            if st.button("🔒 Unlock Editing"):
                st.session_state.show_paywall = True
                st.rerun()
                
            if st.button("Clear List"):
                st.session_state.inventory = []
                st.rerun()

    # --- 2. OPTIMIZATION ---
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

            # TRIGGER 3: SAVING HISTORY
            c_save, c_export = st.columns(2)
            with c_save:
                if st.button("💾 Save to History"):
                    if not is_premium:
                        st.session_state.show_paywall = True
                        st.rerun()
                    else:
                        st.session_state.history.append({"date": datetime.now().strftime("%H:%M"), "profit": max_profit})
                        st.success("Saved!")

            # TRIGGER 4: EXPORTING DATA
            with c_export:
                if is_premium:
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📂 Download CSV", csv, "optiflip.csv", "text/csv")
                else:
                    if st.button("📂 Download CSV (Locked)"):
                        st.session_state.show_paywall = True
                        st.rerun()
            
            # TRIGGER 5: ANALYTICS
            st.write("---")
            if is_premium:
                st.bar_chart(result_df.set_index('name')['cost'])
            else:
                st.info("🔒 Charts are locked for Guest Users.")


# ==========================================
# MAIN EXECUTION CONTROLLER
# ==========================================
if st.session_state.show_paywall:
    paywall_screen()
else:
    main_app()
