import streamlit as st
import pandas as pd
import time
from datetime import datetime

# ==========================================
# CONFIGURATION & STATE
# ==========================================
st.set_page_config(page_title="OptiCalc: Smart Reseller", layout="centered")

# --- DATABASE (MOCK) ---
# We added a 'status' field: 'active' or 'pending'
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "admin", "plan": "Premium", "name": "Admin", "status": "active"},
        "jayward": {"password": "123", "plan": "Premium", "name": "Jayward", "status": "active"} # Sample premium user
    }

# --- PENDING REQUESTS QUEUE ---
if 'pending_requests' not in st.session_state:
    st.session_state.pending_requests = []

# --- SESSION FLAGS ---
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "Guest User", "plan": "Free", "status": "active"}
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_paywall' not in st.session_state:
    st.session_state.show_paywall = False
if 'latest_result' not in st.session_state:
    st.session_state.latest_result = None
if 'run_count' not in st.session_state:
    st.session_state.run_count = 0

# ==========================================
# PART 1: THE ADMIN DASHBOARD (NEW!)
# ==========================================
# ==========================================
# PART 1: THE ADMIN DASHBOARD (FIXED)
# ==========================================
def admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.write("Manage users and approve payments.")
    
    tab1, tab2 = st.tabs(["💰 Payment Requests", "👥 All Users"])
    
    with tab1:
        if st.session_state.pending_requests:
            st.info(f"You have {len(st.session_state.pending_requests)} pending approval(s).")
            
            # Loop through pending requests
            for i, req in enumerate(st.session_state.pending_requests):
                with st.expander(f"Request from: {req['username']} (Ref: {req['ref_num']})", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Name:** {req['name']}")
                        st.write(f"**Email:** {req.get('email', 'N/A')}") 
                        st.write(f"**Plan:** {req['plan']}")
                        st.write(f"**Payment Ref:** `{req['ref_num']}`")
                    with c2:
                        if st.button("✅ Approve", key=f"approve_{i}"):
                            # 1. Create the user in the main DB
                            st.session_state.users_db[req['username']] = {
                                "password": req['password'],
                                "plan": "Premium",
                                "name": req['name'],
                                "email": req.get('email', 'N/A'),
                                "status": "active"
                            }
                            # 2. Remove from pending
                            st.session_state.pending_requests.pop(i)
                            st.success(f"Approved {req['username']}!")
                            time.sleep(1)
                            st.rerun()
                        
                        if st.button("❌ Reject", key=f"reject_{i}"):
                            st.session_state.pending_requests.pop(i)
                            st.error("Request rejected.")
                            time.sleep(1)
                            st.rerun()
        else:
            st.success("No pending payments. All caught up!")

    with tab2:
        st.write("### Registered Users")
        users_list = []
        for u, data in st.session_state.users_db.items():
            users_list.append({
                "Username": u, 
                "Name": data['name'], 
                "Email": data.get('email', '-'), 
                "Plan": data['plan'], 
                "Status": data['status']
            })
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)
        
    if st.button("Logout Admin"):
        st.session_state.user_info = {"name": "Guest User", "plan": "Free", "status": "active"}
        st.rerun()
# ==========================================
# PART 2: THE PAYWALL SCREEN (UPDATED FOR PAYMONGO)
# ==========================================
def paywall_screen():
    st.title("🚀 Unlock OptiCalc Premium")
    st.markdown("You hit a Pro feature! Log in or Upgrade to continue.")
    
    if st.button("← Back to Free Version"):
        st.session_state.show_paywall = False
        st.rerun()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    # --- LOGIN TAB ---
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                db = st.session_state.users_db
                if username in db and db[username]["password"] == password:
                    # Check if they are admin
                    if username == "admin":
                        st.session_state.user_info = db[username]
                        st.session_state.show_paywall = False # Close paywall
                        st.rerun()
                    
                    # Check if they are active
                    elif db[username]['status'] == 'active':
                        st.session_state.user_info = db[username]
                        st.session_state.show_paywall = False
                        st.success(f"Welcome back, {db[username]['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.warning("⚠️ Your account is still PENDING APPROVAL by Admin.")
                else:
                    # Check if they are in the pending queue
                    is_pending = False
                    for req in st.session_state.pending_requests:
                        if req['username'] == username and req['password'] == password:
                            is_pending = True
                            break
                    
                    if is_pending:
                        st.info("🕒 Your payment is currently being verified by the Admin. Please wait.")
                    else:
                        st.error("Invalid Credentials or User does not exist.")

    # --- SIGN UP TAB (PAYMONGO SIMULATION) ---
    with tab2:
        st.write("### ⚡ Create Premium Account")
        
        # Step 1: User Info
        c1, c2 = st.columns(2)
        with c1: new_user = st.text_input("Choose Username")
        with c2: new_pass = st.text_input("Choose Password", type="password")
        new_name = st.text_input("Full Name")
        new_email = st.text_input("Email Address", placeholder="name@example.com")
        
        st.write("---")
        
        # Step 2: PayMongo Simulation
        st.markdown("#### 💳 Payment Method")
        st.info("Please scan the QR code or send **₱149.00** via PayMongo.")
        
        # PayMongo-style UI Box
        with st.container(border=True):
            col_pm_1, col_pm_2 = st.columns([1, 3])
            with col_pm_1:
                # PayMongo Logo (Public URL)
                st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
            with col_pm_2:
                st.write("**Total Amount:** ₱149.00")
                st.caption("Securely processed by PayMongo")
            
            # The "Verification" Field
            ref_num = st.text_input("ENTER PAYMENT REFERENCE NUMBER", placeholder="e.g., PM-1234-5678", help="Check your email or SMS for the Ref No.")
            
            if st.button("✅ Submit for Verification", type="primary", use_container_width=True):
                if new_user and new_pass and new_name and ref_num:
                    # Check if username exists
                    if new_user in st.session_state.users_db:
                        st.error("Username already taken.")
                    else:
                        # Add to Pending Queue
                        st.session_state.pending_requests.append({
                            "username": new_user,
                            "password": new_pass,
                            "name": new_name,
                            "plan": "Premium",
                            "ref_num": ref_num,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        st.balloons()
                        st.success("🎉 Request Sent! The Admin will verify your payment shortly.")
                        st.info(f"Please login after approval. (Ref: {ref_num})")
                else:
                    st.warning("Please fill in all fields and the Reference Number.")

# ==========================================
# PART 3: THE ALGORITHM (SMART QUANTITY)
# ==========================================
def solve_knapsack(inventory_items, capacity):
    # EXPAND ITEMS (Handle "0" as Unlimited)
    expanded_items = []
    
    for item in inventory_items:
        limit = int(item.get('limit', 0))
        cost = int(item['cost'])
        
        if limit == 0:
            limit = int(capacity // cost) if cost > 0 else 0
            limit = min(limit, 50) 
        
        for _ in range(limit):
            expanded_items.append({
                'name': item['name'],
                'cost': cost,
                'profit': int(item['profit']),
                'sell': int(item['sell'])
            })
            
    # STANDARD KNAPSACK
    n = len(expanded_items)
    costs = [item['cost'] for item in expanded_items]
    profits = [item['profit'] for item in expanded_items]
    capacity = int(capacity)
    
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                dp[i][w] = max(profits[i-1] + dp[i-1][w-costs[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    # BACKTRACKING
    selected_items_map = {}
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            item = expanded_items[i-1]
            name = item['name']
            
            if name in selected_items_map:
                selected_items_map[name]['qty'] += 1
                selected_items_map[name]['total_cost'] += item['cost']
                selected_items_map[name]['total_profit'] += item['profit']
            else:
                selected_items_map[name] = {
                    'name': name,
                    'qty': 1,
                    'cost_per_unit': item['cost'],
                    'sell_per_unit': item['sell'],
                    'total_cost': item['cost'],
                    'total_profit': item['profit']
                }
            w -= item['cost']

    return dp[n][capacity], list(selected_items_map.values())

# ==========================================
# PART 4: MAIN APP
# ==========================================
def main_app():
    user = st.session_state.user_info
    
    # --- IF ADMIN, SHOW ADMIN DASHBOARD ---
    if user['name'] == "Admin":
        admin_dashboard()
        return  # Stop here, don't show the reseller dashboard

    plan = user['plan']
    is_premium = plan == "Premium"
    
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
            st.session_state.user_info = {"name": "Guest User", "plan": "Free", "status": "active"}
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
        if st.sidebar.button("🔓 Login | Sign Up"):
            st.session_state.show_paywall = True
            st.rerun()

    # --- DASHBOARD ---
    st.title("📈 OptiCalc Dashboard")
    st.subheader("1. Market Scouting")
    
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1: name_input = st.text_input("Item Name")
    with c2: cost_input = st.number_input("Cost (₱)", min_value=0, step=100)
    with c3: sell_input = st.number_input("Sell Price (₱)", min_value=0, step=100)
    with c4: 
        limit_input = st.number_input(
            "Max Limit (0 = Auto)", 
            min_value=0, 
            value=0, 
            help="Leave at 0 if you want to buy as many as your budget allows. Only enter a number if you have a limit (e.g., 20 sure buyers)."
        )

    if st.button("Add Item"):
        if not is_premium and len(st.session_state.inventory) >= 5:
            st.session_state.show_paywall = True
            st.rerun()
        elif name_input and cost_input > 0:
            profit = sell_input - cost_input
            st.session_state.inventory.append({
                "name": name_input, 
                "cost": int(cost_input), 
                "sell": int(sell_input), 
                "profit": int(profit),
                "limit": int(limit_input)
            })
            limit_display = "Unlimited" if limit_input == 0 else limit_input
            st.success(f"Added {name_input} (Limit: {limit_display})")
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

    if st.button("🚀 Run Analysis (Best Mix)", type="primary"):
        if not is_premium and st.session_state.run_count >= FREE_RUN_LIMIT:
            st.session_state.show_paywall = True
            st.rerun()
        elif not st.session_state.inventory:
            st.warning("List is empty.")
        else:
            if not is_premium:
                st.session_state.run_count += 1
            
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

    # --- RESULTS ---
    if st.session_state.latest_result:
        res = st.session_state.latest_result
        
        st.success("Optimization Complete!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Investment", f"₱{res['total_cost']:,.0f}")
        m2.metric("Total Profit", f"₱{res['max_profit']:,.0f}")
        m3.metric("ROI", f"{res['roi']:.1f}%")

        st.write("### 📋 Recommended Quantity to Buy")
        result_df = pd.DataFrame(res['best_items'])
        
        if not result_df.empty:
            result_df = result_df[['qty', 'name', 'cost_per_unit', 'total_cost', 'total_profit']]
            result_df.columns = ['Rec. Qty', 'Item Name', 'Unit Cost', 'Total Cost', 'Expected Profit']
            st.dataframe(result_df, use_container_width=True)
        else:
            st.warning("Budget is too low.")

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
                st.download_button("📂 Download CSV file", csv, "optiflip_po.csv", "text/csv")
            else:
                if st.button("📂 Download CSV file"):
                    st.session_state.show_paywall = True
                    st.rerun()
        
        st.write("---")
        st.subheader("3. Visual Analytics")
        
        # ==============================================================
        # NEW: BLURRED ANALYTICS (Using Unsplash Image for Reliability)
        # ==============================================================
        if is_premium:
            if not result_df.empty:
                st.caption("✅ Portfolio Diversification")
                st.bar_chart(result_df.set_index('Item Name')['Total Cost'])
            else:
                st.info("Run the optimization to see charts.")
        else:
            # We use a HIGH QUALITY public financial chart image.
            # This is safer than Google Drive because it never gets blocked.
            safe_image_url = "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1000&q=80"

            st.markdown(f"""
<div style="
    position: relative;
    width: 100%;
    height: 300px;
    border-radius: 12px;
    overflow: hidden;
    background-image: url('{safe_image_url}');
    background-size: cover;
    background-position: center;
">
    <div style="
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(6px);
    "></div>
    
    <div style="
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        width: 280px;
    ">
        <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
        <h3 style="margin: 0; color: #333; font-size: 20px;">Unlock Analytics</h3>
        <p style="margin: 8px 0 0 0; color: #666; font-size: 13px;">View profit trends & ROI charts.</p>
    </div>
</div>
<br>
""", unsafe_allow_html=True)
            
            if st.button("🚀 Go to Premium", use_container_width=True, type="primary", key="analytics_btn"):
                st.session_state.show_paywall = True
                st.rerun()

# ==========================================
# EXECUTION
# ==========================================
if st.session_state.show_paywall:
    paywall_screen()
else:
    main_app()





