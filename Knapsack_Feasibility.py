import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ==========================================
# CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="OptiCalc: Smart Reseller", layout="centered")

# --- DATABASE (MOCK) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "admin", "plan": "Premium", "name": "Engr. Jayward Balinas"}
    }

# --- SESSION FLAGS ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "Guest User", "plan": "Free"}
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_paywall' not in st.session_state:
    st.session_state.show_paywall = False
if 'payment_verified' not in st.session_state:
    st.session_state.payment_verified = False

# [NEW] Store the Latest Analysis Result here so it persists!
if 'latest_result' not in st.session_state:
    st.session_state.latest_result = None

# ==========================================
# PART 1: THE "GRAMMARLY" PAYWALL SCREEN
# ==========================================
def paywall_screen():
    st.title("🚀 Unlock OptiCalc Premium")
    st.markdown("You hit a Pro feature! Log in or Upgrade to continue.")
    
    if st.button("← Back to Free Version"):
        st.session_state.show_paywall = False
        st.rerun()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Log In (Existing User)", "Upgrade Now (Sign Up)"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                db = st.session_state.users_db
                if username in db and db[username]["password"] == password:
                    st.session_state.user_info = db[username]
                    st.session_state.show_paywall = False
                    st.success(f"Welcome back, {db[username]['name']}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

    with tab2:
        st.write("### ⚡ Create Premium Account")
        new_user = st.text_input("Choose Username")
        new_pass = st.text_input("Choose Password", type="password")
        new_name = st.text_input("Your Name")
        
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
                st.session_state.users_db[new_user] = {
                    "password": new_pass, "plan": "Premium", "name": new_name
                }
                st.session_state.user_info = st.session_state.users_db[new_user]
                st.session_state.show_paywall = False
                st.success("Welcome to Premium!")
                st.session_state.payment_verified = False
                time.sleep(1)
                st.rerun()

# ==========================================
# PART 2: THE ALGORITHM
# ==========================================
def solve_knapsack(items, capacity):
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
# PART 3: MAIN APP (FIXED LOGIC)
# ==========================================
def main_app():
    user = st.session_state.user_info
    plan = user['plan']
    is_premium = plan == "Premium"
    
    # --- SIDEBAR HISTORY ---
    st.sidebar.title(f"👤 {user['name']}")
    if is_premium:
        st.sidebar.caption("👑 Premium Member")
        st.sidebar.divider()
        st.sidebar.subheader("📜 History Log")
        
        if st.session_state.history:
            for i, record in enumerate(reversed(st.session_state.history)):
                with st.sidebar.expander(f"{record['date']} - ₱{record['profit']}"):
                    st.write(f"**Budget:** ₱{record['budget']}")
                    st.write("**Items:**")
                    for item in record['items']:
                        st.text(f"- {item['name']}")
        else:
            st.sidebar.info("No saved calculations yet.")
            
        st.sidebar.divider()
        if st.sidebar.button("Log Out"):
            st.session_state.user_info = {"name": "Guest User", "plan": "Free"}
            st.session_state.latest_result = None # Clear result on logout
            st.rerun()
    else:
        st.sidebar.caption("Guest Mode (Free)")
        if st.sidebar.button("🔓 Login / Upgrade"):
            st.session_state.show_paywall = True
            st.rerun()

    # --- MAIN DASHBOARD ---
    st.title("📈 OptiCalc Dashboard")
    st.subheader("1. Market Scouting")
    
    c1, c2, c3 = st.columns(3)
    with c1: name_input = st.text_input("Item Name")
    with c2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with c3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)

    if st.button("Add Item"):
        if not is_premium and len(st.session_state.inventory) >= 5:
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
        if is_premium:
            st.caption("✨ **Pro Mode:** Edit cells directly.")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor")
            edited_df['profit'] = edited_df['sell'] - edited_df['cost']
            st.session_state.inventory = edited_df.to_dict('records')
        else:
            st.dataframe(df, use_container_width=True)
            if st.button("🔒 Unlock Editing"):
                st.session_state.show_paywall = True
                st.rerun()
            if st.button("Clear List"):
                st.session_state.inventory = []
                st.rerun()

    # --- 2. OPTIMIZATION ENGINE ---
    st.divider()
    st.subheader("2. Optimization Engine")
    budget = st.number_input("Total Capital (₱)", min_value=0, value=10000, step=500)

    # --- BUTTON 1: RUN ANALYSIS ---
    if st.button("🚀 Run Analysis", type="primary"):
        if not st.session_state.inventory:
            st.warning("List is empty.")
        else:
            # 1. Calculate
            max_profit, best_items = solve_knapsack(st.session_state.inventory, int(budget))
            total_cost = sum(i['cost'] for i in best_items)
            roi = (max_profit / total_cost * 100) if total_cost > 0 else 0
            
            # 2. SAVE TO SESSION STATE (This fixes the disappearing button issue!)
            st.session_state.latest_result = {
                "max_profit": max_profit,
                "best_items": best_items,
                "total_cost": total_cost,
                "roi": roi,
                "budget": budget
            }

    # --- DISPLAY RESULTS (Outside the button block) ---
    # We check if a result exists in memory. If yes, we show it.
    if st.session_state.latest_result:
        res = st.session_state.latest_result
        
        st.success("Analysis Complete!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Investment", f"₱{res['total_cost']:,.0f}")
        m2.metric("Profit", f"₱{res['max_profit']:,.0f}")
        m3.metric("ROI", f"{res['roi']:.1f}%")

        result_df = pd.DataFrame(res['best_items'])
        st.dataframe(result_df, use_container_width=True)

        # --- BUTTON 2: SAVE TO HISTORY (Now safe outside the other button) ---
        c_save, c_export = st.columns(2)
        
        with c_save:
            if st.button("💾 Save to History"):
                if not is_premium:
                    st.session_state.show_paywall = True
                    st.rerun()
                else:
                    st.session_state.history.append({
                        "date": datetime.now().strftime("%H:%M:%S"),
                        "budget": res['budget'],
                        "profit": res['max_profit'],
                        "items": res['best_items']
                    })
                    st.success("Saved!")
                    time.sleep(0.5)
                    st.rerun()

        with c_export:
            if is_premium:
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("📂 Download CSV", csv, "optiflip.csv", "text/csv")
            else:
                if st.button("📂 Download CSV"):
                    st.session_state.show_paywall = True
                    st.rerun()
        
        st.write("---")
        if is_premium:
            st.bar_chart(result_df.set_index('name')['cost'])
        else:
            st.info("🔒 Charts are locked for Guest Users.")

# ==========================================
# EXECUTION
# ==========================================
if st.session_state.show_paywall:
    paywall_screen()
else:
    main_app()

