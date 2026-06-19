with open('telegram_bot.py', 'r', encoding='utf-8') as f:
    code = f.read()
code = code.replace('?onu_id={onu_id}"}', '?onu_id={onu_id}&olt_id={olt_id}"}')
with open('telegram_bot.py', 'w', encoding='utf-8') as f:
    f.write(code)
