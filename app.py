import streamlit as st
import plotly.express as px
from datetime import datetime, date
import pandas as pd
from collections import defaultdict

class ExpenseManager:
    def __init__(self):
        self.initialize_session_state()
        self.setup_page_config()
        self.apply_custom_css()
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if "expenses" not in st.session_state:
            st.session_state.expenses = []
        if "categories" not in st.session_state:
            st.session_state.categories = set(["Food", "Transport", "Entertainment", "Bills", "Shopping", "Others"])
        if "total_expenses" not in st.session_state:
            st.session_state.total_expenses = 0.0
        if "reset_state" not in st.session_state:
            st.session_state.reset_state = False
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Expense Manager Pro",
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def apply_custom_css(self):
        """Apply custom CSS styling"""
        st.markdown("""
            <style>
            .main { padding: 2rem; }
            .stButton>button {
                width: 100%;
                border-radius: 10px;
                height: 3em;
                background-color: #4CAF50;
                color: white;
            }
            .expense-card {
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                background-color: white;
                color: black;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .metric-card {
                background-color: #f8f9fa;
                color: black;
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .category-pill {
                background-color: #e9ecef;
                color: black;
                padding: 0.4rem 0.8rem;
                margin-top: 0.5rem;
                text-align: center;
                border-radius: 15px;
                font-size: 0.9em;
            }
            .reset-button {
                background-color: #dc3545 !important;
                color: white !important;
                margin-top: 1rem;
            }
            .reset-message {
                padding: 1rem;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 5px;
                color: #721c24;
                margin: 1rem 0;
            }
            </style>
        """, unsafe_allow_html=True)

    def add_expense(self, amount, category, description, expense_date):
        """Add a new expense with validation"""
        try:
            expense = {
                "amount": float(amount),
                "category": str(category),
                "description": str(description),
                "date": expense_date,
                "timestamp": datetime.now()
            }
            # Add the expense to the session state
            st.session_state.expenses.append(expense)
            
            # Update the total expenses directly in the session state
            st.session_state.total_expenses += float(amount)
            
            return True
        except Exception as e:
            st.error(f"Error adding expense: {str(e)}")
            return False

    def get_expense_metrics(self):
        """Calculate expense metrics safely"""
        try:
            if not st.session_state.expenses:
                return 0, 0, 0
            
            total = sum(float(expense["amount"]) for expense in st.session_state.expenses)
            avg = total / len(st.session_state.expenses) if st.session_state.expenses else 0
            max_expense = max(float(expense["amount"]) for expense in st.session_state.expenses)
            return total, avg, max_expense
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
            return 0, 0, 0

    def render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.title("💰 ExpenseTracker Pro")
            menu = ["Dashboard", "Add Expense", "View Expenses", "Expense Analysis", "Settings"]
            st.session_state.current_page = st.radio("Navigation", menu, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("### Quick Stats")
            total, _, _ = self.get_expense_metrics()
            st.metric("Total Expenses", f"${total:,.2f}")

    def render_dashboard(self):
        """Render dashboard page"""
        st.title("📊 Expense Dashboard")
        st.markdown("Welcome to ExpenseTracker Pro! Use the navigation menu to manage your expenses.")
        total, avg, max_exp = self.get_expense_metrics()
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        for col, (title, value) in zip(
            [col1, col2, col3],
            [("Total Expenses", total), ("Average Expense", avg), ("Highest Expense", max_exp)]
        ):
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>{title}</h3>
                        <h2>${value:,.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)

        # Recent expenses and charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Recent Expenses")
            if st.session_state.expenses:
                for expense in reversed(st.session_state.expenses[-5:]):
                    st.markdown(f"""
                        <div class="expense-card">
                            <h3>${float(expense['amount']):,.2f}</h3>
                            <span class="category-pill">{expense['category']}</span>
                            <p>{expense['description']}</p>
                            <small>{expense['date'].strftime('%Y-%m-%d')}</small>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No expenses recorded yet!")

        with col2:
            if st.session_state.expenses:
                df = pd.DataFrame(st.session_state.expenses)
                fig = px.pie(df, values='amount', names='category', title='Expenses by Category')
                st.plotly_chart(fig, use_container_width=True)

    def render_add_expense(self):
        """Render add expense page"""
        st.title("➕ Add New Expense")
        
        with st.form("expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input("Amount ($)", min_value=0.01, format="%.2f", step=0.01)
                category = st.selectbox("Category", sorted(list(st.session_state.categories)))
            
            with col2:
                expense_date = st.date_input("Date", value=date.today())
                description = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Expense 💰")
            if submitted:
                if description:
                    success = self.add_expense(amount, category, description, expense_date)
                    if success:
                        st.success("✅ Expense added successfully!")
                    else:
                        st.error("Error adding the expense. Please try again.")
                else:
                    st.error("Please provide a description for the expense.")

    def render_view_expenses(self):
        """Render expenses in a tabular format"""
        st.title("📋 View All Expenses")

        if st.session_state.expenses:
            # Convert expense data to a DataFrame
            df = pd.DataFrame(st.session_state.expenses)
            
            # Ensure the 'date' column is in datetime format
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # Format date for better readability
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')

            # Rename columns for display
            df = df.rename(columns={
                'amount': 'Amount ($)',
                'category': 'Category',
                'description': 'Description',
                'date': 'Date'
            })

            # Display DataFrame in a tabular format
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No expenses to display yet! Start adding some.")

    def render_expense_analysis(self):
        """Render expense analysis page"""
        st.title("📈 Expense Analysis")
        st.info("Expense analysis features are coming soon!")
        if st.session_state.expenses:
            df = pd.DataFrame(st.session_state.expenses)
            
            # Time series analysis
            fig1 = px.line(df, x='date', y='amount', title='Expense Trend Over Time')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Category breakdown
            col1, col2 = st.columns(2)
            with col1:
                fig2 = px.bar(df.groupby('category')['amount'].sum().reset_index(), 
                             x='category', y='amount', title='Expenses by Category')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                fig3 = px.box(df, x='category', y='amount', title='Expense Distribution by Category')
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Add some expenses to see the analysis!")

    def render_settings(self):
        """Render settings page"""
        st.title("⚙️ Settings")
        
        # Category management
        st.subheader("Manage Categories")
        new_category = st.text_input("Add New Category")
        if st.button("Add Category"):
            if new_category and new_category not in st.session_state.categories:
                st.session_state.categories.add(new_category)
                st.success(f"Added category: {new_category}")
        
        # Display categories
        st.markdown("### Existing Categories")
        categories_cols = st.columns(3)
        for idx, category in enumerate(sorted(st.session_state.categories)):
            with categories_cols[idx % 3]:
                st.write(f"- {category}")

    def render_reset_section(self):
        """Render the reset section"""
        st.markdown(f"""
            <div class="reset-message">
                <h3>⚠️ Warning!</h3>
                <p>This will reset all your expenses and settings!</p>
                <button class="reset-button" onClick="window.location.reload()">Reset Now</button>
            </div>
        """, unsafe_allow_html=True)

    def run(self):
        """Run the ExpenseManager app"""
        self.render_sidebar()
        
        if st.session_state.current_page == "Dashboard":
            self.render_dashboard()
        elif st.session_state.current_page == "Add Expense":
            self.render_add_expense()
        elif st.session_state.current_page == "View Expenses":
            self.render_view_expenses()
        elif st.session_state.current_page == "Expense Analysis":
            self.render_expense_analysis()
        elif st.session_state.current_page == "Settings":
            self.render_settings()

# Run the app
if __name__ == "__main__":
    app = ExpenseManager()
    app.run()
