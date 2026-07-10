SELECT 
    session_id AS "Session ID", 
    message_id AS "Message ID", 
    role AS "Sender", 
    content AS "Message Content", 
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS "Timestamp"
FROM SYSTEM.chat_history 
ORDER BY session_id ASC, created_at ASC;
