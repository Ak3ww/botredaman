with open('C:/BotRedaman/scratch/build_installer.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('${TELE_TOKEN}', '${{TELE_TOKEN}}')
c = c.replace('${TELE_CHAT_ID}', '${{TELE_CHAT_ID}}')
c = c.replace('${DASH_URL}', '${{DASH_URL}}')
c = c.replace('${BULK_MIN}', '${{BULK_MIN}}')
c = c.replace('${MK_HOST}', '${{MK_HOST}}')
c = c.replace('${MK_USER}', '${{MK_USER}}')
c = c.replace('${MK_PASS}', '${{MK_PASS}}')

# Fix colors
c = c.replace('${BLUE}', '${{BLUE}}')
c = c.replace('${NC}', '${{NC}}')
c = c.replace('${GREEN}', '${{GREEN}}')
c = c.replace('${RED}', '${{RED}}')
c = c.replace('${YELLOW}', '${{YELLOW}}')

with open('C:/BotRedaman/scratch/build_installer.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("Fixed!")
