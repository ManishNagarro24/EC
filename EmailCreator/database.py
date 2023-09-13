import pyodbc
from config import DB_CONFIG

def create_connection():
    config = DB_CONFIG
    connection_string = (
        f"DRIVER={config['driver']};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"Trusted_Connection={config['trusted_connection']};"
    )
    return pyodbc.connect(connection_string)

def save_conversation(chat_history):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO conversations_history (organization_id, organization_name, chat_history) VALUES (?, ?, ?)",
                   (1, 'WWF', chat_history))
    connection.commit()
    cursor.close()
    connection.close()

def get_user_conversations(organization_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT prompt, response FROM conversations_history WHERE organization_id = ?", (organization_id,))
    conversations = cursor.fetchall()
    cursor.close()
    connection.close()
    return conversations
