import mysql.connector
import os
import random
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="config/ca.pem",
    )

def get_random_case():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT ic.case_id, ic.case_date, ic.price_at_case, ic.cagr_as_of_case,
               ic.volatility_as_of_case, ic.outcome_return_1y, ic.outcome_return_to_date,
               c.name AS company_name
        FROM investment_cases ic
        JOIN companies c ON ic.company_id = c.company_id
        """
    )
    all_cases = cursor.fetchall()
    cursor.close()
    conn.close()

    if not all_cases:
        return None
    return random.choice(all_cases)


def evaluate_decision(decision, outcome_return_1y):
    outcome_return_1y = float(outcome_return_1y)

    if decision == "BUY":
        return outcome_return_1y > 10
    elif decision == "AVOID":
        return outcome_return_1y < -10
    elif decision == "HOLD":
        return -10 <= outcome_return_1y <= 10
    return False


def save_decision(case_id, decision, was_correct):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_decisions (case_id, decision, was_correct) VALUES (%s, %s, %s)",
        (case_id, decision, was_correct),
    )
    conn.commit()
    cursor.close()
    conn.close()
