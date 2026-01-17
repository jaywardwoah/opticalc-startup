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
if 'latest_result' not in st.session_state:
    st.session_state.latest_result = None
if 'run_count' not in st.session_state:
    st.session_state.run_count = 0

# ==========================================
# PART 1: THE PAYWALL SCREEN
# ==========================================
def paywall_screen():
    st.title("🚀 Unlock OptiFlip Premium")
    st.markdown("You hit a Pro feature! Log in or Upgrade to continue.")
    
    if st.button("← Back to Free Version"):
        st.session_state.show_paywall = False
        st.rerun()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Log In", "Upgrade Now"])
    
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
        with st.expander("💸 Proceed to Payment", expanded=True):
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
                st.success("Welcome!")
                st.session_state.payment_verified = False
                time.sleep(1)
                st.rerun()

# ==========================================
# PART 2: THE ALGORITHM (UNBOUNDED KNAPSACK)
# ==========================================
def solve_knapsack(items, capacity):
    # This is the "Unbounded" version: items can be selected multiple times
    n = len(items)
    costs = [int(item['cost']) for item in items]
    profits = [int(item['profit']) for item in items]
    capacity = int(capacity)
    
    # dp[w] stores the max profit for capacity w
    dp = [0 for _ in range(capacity + 1)]
    
    # For reconstruction: keep track of which item was added at each weight step
    # item_choice[w] = index of the item that maximized profit at weight w
    item_choice = [-1] * (capacity + 1)

    for w in range(1, capacity + 1):
        for i in range(n):
            if costs[i] <= w:
                # If adding item i gives more profit than current best at weight w
                if dp[w - costs[i]] + profits[i] > dp[w]:
                    dp[w] = dp[w - costs[i]] + profits[i]
                    item_choice[w] = i

    # Reconstruct the solution (Backtracking)
    selected_items_map = {} # To count quantities: {"Item A": 3, "Item B": 2}
    w = capacity
    
    while w > 0 and item_choice[w] != -1:
        i = item_choice[w]
        item_name = items[i]['name']
        
        # Add to count
        if item_name in selected_items_map:
            selected_items_map[item_name]['qty'] += 1
            selected_items_map[item_name]['total_cost'] += costs[i]
            selected_items_map[item_name]['total_profit'] += profits[i]
        else:
            selected_items_map[item_name] = {
                'name': item_name,
                'qty': 1,
                'cost_per_unit': costs[i],
                'sell_per_unit': items[i]['sell'],
                'total_cost': costs[i],
                'total_profit': profits[i]
            }
        w -= costs[i]

    # Convert map back to list for display
    final_list = list(selected_items_map.values())
    return dp[capacity], final_list

# ==========================================
# PART 3: MAIN APP (UPDATED DISPLAY)
# ==========================================
def main_app():
    user = st.session_state.user_info
    plan = user['plan']
    is_premium = plan == "Premium"
    
    # --- USAGE LIMIT ---
    FREE_RUN_LIMIT = 3
    
    # --- SIDEBAR ---
    st.sidebar.title(f"👤 {user['name']}")
    if is_premium:
        st.sidebar.caption("👑 Premium Member")
        st.sidebar.divider()
        st.sidebar.subheader("📜 History Log")
        if st.session_state.history:
            for i, record in enumerate(reversed(st.session_state.history)):
                with st.sidebar.expander(f"{record['date']} - ₱{record['profit']}"):
                    st.write(f"**Budget:** ₱{record['budget']}")
                    st.write("**Strategy:**")
                    for item in record['items']:
                        st.text(f"- {item['qty']}x {item['name']}")
        else:
            st.sidebar.info("Empty Log.")
            
        st.sidebar.divider()
        if st.sidebar.button("Log Out"):
            st.session_state.user_info = {"name": "Guest User", "plan": "Free"}
            st.session_state.latest_result = None
            st.session_state.run_count = 0
            st.rerun()
    else:
        st.sidebar.caption("Guest Mode (Free)")
        runs_left = FREE_RUN_LIMIT - st.session_state.run_count
        st.sidebar.write(f"**Free Runs Left: {runs_left}/{FREE_RUN_LIMIT}**")
        if runs_left > 0:
            st.sidebar.progress(runs_left / FREE_RUN_LIMIT)
        else:
            st.sidebar.error("Limit Reached!")
        
        st.sidebar.divider()
        if st.sidebar.button("🔓 Login / Upgrade"):
            st.session_state.show_paywall = True
            st.rerun()

    # --- DASHBOARD ---
    st.title("📈 OptiFlip Dashboard")
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

    if st.button("🚀 Run Analysis (Max Quantity)", type="primary"):
        if not is_premium and st.session_state.run_count >= FREE_RUN_LIMIT:
            st.session_state.show_paywall = True
            st.rerun()
        elif not st.session_state.inventory:
            st.warning("List is empty.")
        else:
            if not is_premium:
                st.session_state.run_count += 1
            
            # RUN UNBOUNDED KNAPSACK
            max_profit, best_items = solve_knapsack(st.session_state.inventory, int(budget))
            total_cost = sum(i['total_cost'] for i in best_items)
            roi = (max_profit / total_cost * 100) if total_cost > 0 else 0
            
            st.session_state.latest_result = {
                "max_profit": max_profit,
                "best_items": best_items,
                "total_cost": total_cost,
                "roi": roi,
                "budget": budget
            }
            st.rerun()

    # --- RESULTS DISPLAY ---
    if st.session_state.latest_result:
        res = st.session_state.latest_result
        
        st.success("Analysis Complete!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Investment", f"₱{res['total_cost']:,.0f}")
        m2.metric("Total Profit", f"₱{res['max_profit']:,.0f}")
        m3.metric("ROI", f"{res['roi']:.1f}%")

        # DISPLAY TABLE WITH QUANTITY
        st.write("### 📋 Recommended Purchase Order")
        result_df = pd.DataFrame(res['best_items'])
        
        # Reorder columns for clarity
        if not result_df.empty:
            result_df = result_df[['qty', 'name', 'cost_per_unit', 'total_cost', 'total_profit']]
            result_df.columns = ['Qty', 'Item Name', 'Unit Cost', 'Total Cost', 'Expected Profit']
            st.dataframe(result_df, use_container_width=True)
        else:
            st.warning("Budget is too low to buy any items.")

        # --- SAVE & EXPORT ---
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
                st.download_button("📂 Download PO (CSV)", csv, "optiflip_po.csv", "text/csv")
            else:
                if st.button("📂 Download PO (Locked)"):
                    st.session_state.show_paywall = True
                    st.rerun()
        
        # --- CHARTS ---
        st.write("---")
        st.subheader("3. Visual Analytics")
        if is_premium:
            if not result_df.empty:
                st.bar_chart(result_df.set_index('Item Name')['Total Cost'])
                st.caption("✅ Cost Allocation per Item Type")
        else:
            st.image("blurred_chart.png", use_container_width=True)
            if st.button("🔓 Unlock Analytics"):
                st.session_state.show_paywall = True
                st.rerun()

# ==========================================
# EXECUTION
# ==========================================
if st.session_state.show_paywall:
    paywall_screen()
else:
    main_app()
