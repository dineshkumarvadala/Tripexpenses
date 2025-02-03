from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

FILEPATH = "budget_data.json"

# Load budget data from a JSON file
def load_budget_data():
    try:
        with open(FILEPATH, "r") as file:
            data = json.load(file)
            return int(data.get("initial_budget", 0)), data.get("expenses", [])
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 0, []

# Save budget data to a JSON file
def save_budget_data(initial_budget, expenses):
    data = {"initial_budget": initial_budget, "expenses": expenses}
    with open(FILEPATH, "w") as file:
        json.dump(data, file, indent=4)

# Initialize budget and expenses
initial_budget, expenses = load_budget_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_budget", methods=["POST"])
def set_budget():
    global initial_budget, expenses
    data = request.json
    initial_budget = int(data.get("budget", 0))  # Ensure budget is an integer
    expenses = []  # Reset expenses when setting a new budget
    save_budget_data(initial_budget, expenses)
    return jsonify({"message": "Budget set successfully!", "budget": initial_budget})

@app.route("/add_expenses", methods=["POST"])
def add_expenses():
    global expenses
    data = request.json
    new_expenses = data.get("expenses", [])  # Expecting a list of expenses

    if not isinstance(new_expenses, list) or not new_expenses:
        return jsonify({"error": "Invalid expense data"}), 400

    for expense in new_expenses:
        description = expense.get("description")
        amount = expense.get("amount", 0)

        if not description or amount <= 0:
            return jsonify({"error": f"Invalid data for expense: {description}"}), 400

        expenses.append({"description": description, "amount": amount})

    save_budget_data(initial_budget, expenses)

    return jsonify({"message": "Expenses added successfully!", "expenses": expenses})

@app.route("/get_budget_details", methods=["GET"])
def get_budget_details():
    total_spent = sum(expense["amount"] for expense in expenses)
    remaining_budget = initial_budget - total_spent  # Now guaranteed to be integer operations
    return jsonify({
        "total_budget": initial_budget,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "expenses": expenses
    })

if __name__ == "__main__":
    app.run(debug=True)
