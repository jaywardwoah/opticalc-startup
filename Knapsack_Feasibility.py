import streamlit as st
import pandas as pd

# ==========================================
# PART 1: THE ALGORITHM (THE BRAIN)
# ==========================================
def solve_knapsack(items, capacity):
    """
    Solves the 0/1 Knapsack Problem using Dynamic Programming.
    items: list of dictionaries {'name', 'cost', 'profit'}
    capacity: integer (Budget)
    """
    n = len(items)
    costs = [item['cost'] for item in items]
    profits = [item['profit'] for item in items]
    
    # Create the DP table
    # dp[i][w] stores the max profit for first i items with weight limit w
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if costs[i-1] <= w:
                # Max of (including the item) vs (excluding the item)
                dp[i][w] = max(profits[i-1] + dp[i-1][w-costs[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    # Backtracking to find WHICH items were selected
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(items[i-1])
            w -= costs[i-1]

    return dp[n][capacity], selected_items

# ==========================================
# PART 2: THE INTERFACE (THE LOOKS)
# ==========================================

# Page Config
st.set_page_config(page_title="OptiCalc: Reseller DSS", layout="centered")

# Initialize Session State (To remember items added)
if 'inventory' not in st.session_state:
    st.session_state.inventory = []

# --- SIDEBAR: BUSINESS MODEL SIMULATION ---
st.sidebar.title("⚙️ System Settings")
st.sidebar.info("Feasibility Study Simulation Mode")
user_plan = st.sidebar.radio("Select User Plan:", ["Free Tier", "Premium Tier (₱99/mo)"])

# Limit Simulation
ITEM_LIMIT = 5 if user_plan == "Free Tier" else 999
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Current Limits:**\n\nItems Allowed: `{ITEM_LIMIT}`")

# --- MAIN PAGE ---
st.title("📈 OptiCalc")
st.subheader("Algorithmic Profit Maximizer for Resellers")
st.markdown("Enter the items you found in the market, and let the AI decide what to buy.")

# --- MODULE 1: INPUT ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    name_input = st.text_input("Item Name", placeholder="e.g. Nike Dunk")
with col2:
    cost_input = st.number_input("Buying Cost (₱)", min_value=0, step=100)
with col3:
    sell_input = st.number_input("Est. Selling Price (₱)", min_value=0, step=100)

# Button to Add Item
if st.button("Add Item to List"):
    # MARKETABILITY CHECK: Enforce Freemium Limits
    if len(st.session_state.inventory) >= ITEM_LIMIT:
        st.error(f"🔒 LIMIT REACHED! You are on the {user_plan}. Please upgrade to add more items.")
    elif name_input and cost_input > 0:
        profit = sell_input - cost_input
        st.session_state.inventory.append({
            "name": name_input,
            "cost": int(cost_input),
            "sell": int(sell_input),
            "profit": int(profit)
        })
        st.success(f"Added {name_input}!")
    else:
        st.warning("Please enter valid item details.")

# Display Current List
if st.session_state.inventory:
    st.markdown("### 📋 Current Opportunities")
    df = pd.DataFrame(st.session_state.inventory)
    st.dataframe(df, use_container_width=True)
    
    # Clear Button
    if st.button("Clear List"):
        st.session_state.inventory = []
        st.rerun()

# --- MODULE 2: OPTIMIZATION ---
st.divider()
st.header("💰 Capital Budgeting")

budget_input = st.number_input("What is your Total Budget? (₱)", min_value=0, step=500, value=10000)

if st.button("🚀 RUN OPTIMIZATION", type="primary"):
    if not st.session_state.inventory:
        st.warning("Please add items first.")
    else:
        # Run the Algorithm
        max_profit, best_items = solve_knapsack(st.session_state.inventory, int(budget_input))
        
        # Calculate totals for result
        total_cost = sum(item['cost'] for item in best_items)
        roi = (max_profit / total_cost * 100) if total_cost > 0 else 0
        
        # --- MODULE 3: OUTPUT ---
        st.success("✅ Optimal Buying Strategy Generated!")
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Investment", f"₱{total_cost:,.2f}")
        m2.metric("Projected Profit", f"₱{max_profit:,.2f}", delta_color="normal")
        m3.metric("Est. ROI", f"{roi:.1f}%")
        
        st.subheader("🛒 You Should Buy These Items:")
        
        if best_items:
            result_df = pd.DataFrame(best_items)
            st.dataframe(result_df[['name', 'cost', 'sell', 'profit']], use_container_width=True)
            
            # Recommendation Text
            st.info(f"💡 **Analysis:** By spending **₱{total_cost}** out of your **₱{budget_input}** budget, you maximize your profit to **₱{max_profit}**. Any other combination would yield less money or exceed your capital.")
        else:
            st.warning("Your budget is too low to buy any of the listed items.")

# --- FOOTER ---
st.markdown("---")
st.caption("Feasibility Study Prototype | Industrial Engineering Dept.")