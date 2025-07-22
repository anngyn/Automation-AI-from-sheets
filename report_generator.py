import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from notification_handler import send_email_notification
import os

def generate_daily_report(admin_email):
    conn = sqlite3.connect('automation_logs.db')
    df = pd.read_sql_query("SELECT * FROM task_logs", conn)
    conn.close()

    today = datetime.date.today()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    daily_logs = df[df['timestamp'].dt.date == today]

    if daily_logs.empty:
        report_body = "No tasks processed today."
        send_email_notification(admin_email, f"Daily Automation Report - {today}", report_body)
        return

    total_tasks = len(daily_logs)
    successful_tasks = daily_logs[daily_logs['status'] == 'success']
    failed_tasks = daily_logs[daily_logs['status'] == 'failure']

    success_rate = (len(successful_tasks) / total_tasks) * 100 if total_tasks > 0 else 0
    failure_rate = (len(failed_tasks) / total_tasks) * 100 if total_tasks > 0 else 0

    # Generate chart
    labels = ['Success', 'Failure']
    sizes = [len(successful_tasks), len(failed_tasks)]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0) if len(successful_tasks) > 0 and len(failed_tasks) > 0 else (0, 0) # Explode the largest slice

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    chart_filename = f"daily_report_chart_{today}.png"
    plt.title(f"Daily Automation Success/Failure Rates ({today})")
    plt.savefig(chart_filename)
    plt.close(fig1)

    report_body = f"""
    Daily Automation Report - {today}

    Total Tasks Processed: {total_tasks}
    Successful Tasks: {len(successful_tasks)} ({success_rate:.2f}%)
    Failed Tasks: {len(failed_tasks)} ({failure_rate:.2f}%)

    ---
    Details of Failed Tasks:
    """
    if not failed_tasks.empty:
        for index, row in failed_tasks.iterrows():
            report_body += f"\n- Task ID: {row['task_id']}, Description: {row['description']}, Error: {row['error_message']}"
    else:
        report_body += "\nNo failed tasks today."

    print(f"Generated daily report. Chart saved as {chart_filename}. Email body:\n{report_body}")
    # Consider sending email with attachment or referencing an uploaded chart in email body
    send_email_notification(admin_email, f"Daily Automation Report - {today}", report_body)

    if os.path.exists(chart_filename):
        os.remove(chart_filename)

