import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------

st.set_page_config(
    page_title="Fulfillment Hub",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Fulfillment Hub")
st.caption("Order fulfillment control center for XYZ")

# ---------------------------------------------------------
# SAMPLE DATA
# ---------------------------------------------------------

orders = pd.DataFrame([
    [1001, "Aarav", "Wireless Mouse", "Black", "Priority", "Picking", "FastShip", 25, "Today"],
    [1002, "Meera", "Keyboard", "White", "Regular", "Packing", "QuickGo", 48, "Tomorrow"],
    [1003, "Rahul", "USB-C Cable", "1m", "Regular", "Staging", "FastShip", 30, "Today"],
    [1004, "Sara", "Laptop Stand", "Silver", "Priority", "Delayed", "QuickGo", 12, "Today"],
    [1005, "Kabir", "Webcam", "HD", "Regular", "Order Received", "ShipNow", 72, "Tomorrow"],
    [1006, "Ananya", "Wireless Mouse", "White", "Priority", "Waiting Stock", "FastShip", 15, "Today"],
    [1007, "Rohan", "Headphones", "Black", "Regular", "Packed", "ShipNow", 55, "Tomorrow"],
    [1008, "Isha", "Keyboard", "Black", "Priority", "Picking", "QuickGo", 20, "Today"],
    [1009, "Vikram", "USB-C Cable", "2m", "Regular", "Staging", "FastShip", 60, "Tomorrow"],
    [1010, "Nisha", "Laptop Stand", "Black", "Priority", "Packing", "ShipNow", 18, "Today"],
])

orders.columns = [
    "Order ID",
    "Customer",
    "Product",
    "Variant",
    "Priority",
    "Status",
    "Courier",
    "Minutes to Deadline",
    "Deadline"
]

inventory = pd.DataFrame([
    ["Wireless Mouse", "Black", 18, 12, 30],
    ["Wireless Mouse", "White", 3, 20, 25],
    ["Keyboard", "White", 25, 10, 20],
    ["Keyboard", "Black", 12, 15, 20],
    ["USB-C Cable", "1m", 40, 20, 30],
    ["USB-C Cable", "2m", 22, 8, 30],
    ["Laptop Stand", "Silver", 15, 10, 15],
    ["Laptop Stand", "Black", 5, 20, 15],
    ["Webcam", "HD", 30, 15, 20],
    ["Headphones", "Black", 45, 10, 20],
])

inventory.columns = [
    "Product",
    "Variant",
    "Main Warehouse",
    "Secondary Warehouse",
    "Reorder Level"
]

# Calculate total stock and status
inventory["Total Stock"] = (
    inventory["Main Warehouse"] +
    inventory["Secondary Warehouse"]
)

inventory["Stock Status"] = inventory.apply(
    lambda row:
        "🔴 Critical" if row["Main Warehouse"] == 0
        else "🟠 Low" if row["Main Warehouse"] <= row["Reorder Level"]
        else "🟢 Healthy",
    axis=1
)

issues = pd.DataFrame([
    [1, 1004, "Delayed Order", "Order missed expected processing time", "Open"],
    [2, 1006, "Stock Shortage", "Main warehouse does not have enough stock", "Open"],
    [3, 1008, "Priority Risk", "Priority order approaching deadline", "Open"],
    [4, 1003, "Courier Pickup", "Courier pickup pending", "Monitoring"],
])

issues.columns = [
    "Issue ID",
    "Order ID",
    "Issue Type",
    "Description",
    "Status"
]

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("Fulfillment Hub")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "📦 Orders",
        "🏭 Inventory",
        "🚚 Shipping & Staging",
        "⚠️ Issues"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "This application replaces scattered spreadsheets "
    "with one simple fulfillment view."
)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if page == "📊 Dashboard":

    st.header("Operations Dashboard")

    total_orders = len(orders)
    priority_orders = len(
        orders[orders["Priority"] == "Priority"]
    )
    delayed_orders = len(
        orders[orders["Status"] == "Delayed"]
    )
    waiting_stock = len(
        orders[orders["Status"] == "Waiting Stock"]
    )
    ready_pickup = len(
        orders[orders["Status"].isin(["Staging", "Packed"])]
    )

    # KPI CARDS
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Orders", total_orders)
    col2.metric("Priority Orders", priority_orders)
    col3.metric("Delayed", delayed_orders)
    col4.metric("Waiting Stock", waiting_stock)
    col5.metric("Ready for Pickup", ready_pickup)

    st.divider()

    # Priority orders
    st.subheader("🚨 Priority Orders Requiring Attention")

    priority_df = orders[
        (orders["Priority"] == "Priority") |
        (orders["Status"].isin(["Delayed", "Waiting Stock"]))
    ]

    st.dataframe(
        priority_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Status summary
    st.subheader("📈 Order Status")

    status_summary = (
        orders["Status"]
        .value_counts()
        .reset_index()
    )

    status_summary.columns = ["Status", "Orders"]

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.bar_chart(
            status_summary.set_index("Status")
        )

    st.divider()

    # Operational alerts
    st.subheader("⚠️ Operational Alerts")

    if delayed_orders > 0:
        st.warning(
            f"{delayed_orders} order(s) are currently delayed."
        )

    if waiting_stock > 0:
        st.warning(
            f"{waiting_stock} order(s) are waiting for stock."
        )

    low_stock = len(
        inventory[inventory["Stock Status"] != "🟢 Healthy"]
    )

    if low_stock > 0:
        st.info(
            f"{low_stock} inventory item(s) need attention."
        )

# ---------------------------------------------------------
# ORDERS
# ---------------------------------------------------------

elif page == "📦 Orders":

    st.header("Order Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All"] + sorted(orders["Status"].unique())
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "Priority", "Regular"]
        )

    with col3:
        search = st.text_input(
            "Search Order ID / Customer"
        )

    filtered = orders.copy()

    if status_filter != "All":
        filtered = filtered[
            filtered["Status"] == status_filter
        ]

    if priority_filter != "All":
        filtered = filtered[
            filtered["Priority"] == priority_filter
        ]

    if search:
        filtered = filtered[
            filtered["Order ID"].astype(str).str.contains(
                search, case=False
            )
            |
            filtered["Customer"].str.contains(
                search, case=False
            )
        ]

    st.write(
        f"Showing **{len(filtered)}** order(s)"
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Order Processing Flow")

    st.write(
        "Order Received → Picking → Packing → "
        "Staging → Shipping"
    )

    st.caption(
        "Priority orders can be identified quickly and "
        "filtered before they miss their deadline."
    )

# ---------------------------------------------------------
# INVENTORY
# ---------------------------------------------------------

elif page == "🏭 Inventory":

    st.header("Warehouse Inventory")

    st.subheader("Inventory Overview")

    st.dataframe(
        inventory,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🔴 Items Requiring Attention")

    low_inventory = inventory[
        inventory["Stock Status"] != "🟢 Healthy"
    ]

    if len(low_inventory) > 0:
        st.dataframe(
            low_inventory,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("All inventory levels are healthy.")

    st.divider()

    st.subheader("📦 Stock Transfer Suggestions")

    transfer_needed = inventory[
        (inventory["Main Warehouse"] <= inventory["Reorder Level"])
        &
        (inventory["Secondary Warehouse"] > 0)
    ]

    if len(transfer_needed) > 0:

        for _, row in transfer_needed.iterrows():

            suggested_qty = min(
                row["Secondary Warehouse"],
                max(
                    row["Reorder Level"] -
                    row["Main Warehouse"],
                    0
                )
            )

            st.warning(
                f"**{row['Product']} - {row['Variant']}**: "
                f"consider transferring approximately "
                f"**{suggested_qty} units** from secondary "
                f"warehouse."
            )

    else:
        st.success("No immediate stock transfers required.")

# ---------------------------------------------------------
# SHIPPING & STAGING
# ---------------------------------------------------------

elif page == "🚚 Shipping & Staging":

    st.header("Shipping & Staging")

    shipping_orders = orders[
        orders["Status"].isin(
            ["Packing", "Packed", "Staging"]
        )
    ]

    st.subheader("📦 Orders Nearing Courier Pickup")

    st.dataframe(
        shipping_orders,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🚚 Courier Overview")

    courier_summary = (
        orders.groupby("Courier")
        .agg(
            Orders=("Order ID", "count"),
            Avg_Deadline=("Minutes to Deadline", "mean")
        )
        .reset_index()
    )

    courier_summary["Avg_Deadline"] = (
        courier_summary["Avg_Deadline"]
        .round(0)
        .astype(int)
    )

    st.dataframe(
        courier_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.info(
        "The staging view helps the warehouse team see "
        "which packed orders are waiting for courier pickup."
    )

# ---------------------------------------------------------
# ISSUES
# ---------------------------------------------------------

elif page == "⚠️ Issues":

    st.header("Issue Tracker")

    st.write(
        "Centralized issue tracking prevents operational "
        "problems from being handled informally or forgotten."
    )

    issue_filter = st.selectbox(
        "Issue Status",
        ["All"] + sorted(issues["Status"].unique())
    )

    filtered_issues = issues.copy()

    if issue_filter != "All":
        filtered_issues = filtered_issues[
            filtered_issues["Status"] == issue_filter
        ]

    st.dataframe(
        filtered_issues,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Issue Summary")

    issue_summary = (
        issues["Issue Type"]
        .value_counts()
        .reset_index()
    )

    issue_summary.columns = ["Issue Type", "Count"]

    st.bar_chart(
        issue_summary.set_index("Issue Type")
    )

    st.divider()

    st.success(
        "Central issue tracking gives the office and "
        "warehouse teams one place to follow problems "
        "through resolution."
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Fulfillment Hub • Prototype built for XYZ "
    "e-commerce fulfillment operations"
)