import asyncio
import requests
import hashlib
from playwright.async_api import async_playwright

url = 'http://192.168.30.5:8002'
pwd_plain = 'ggclink0lt'
m = hashlib.md5()
m.update(('an3400' + pwd_plain).encode('utf-8'))
pwd_md5 = m.hexdigest()

headers = {'Referer': f'{url}/login.html', 'Connection': 'close', 'User-Agent': 'Mozilla/5.0'}
r = requests.post(f'{url}/setModules', headers=headers, json={'login': {'username': 'root', 'password': pwd_md5}})
cookie_dict = r.cookies.get_dict()
token = r.headers.get('token', '')

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{'name': k, 'value': v, 'domain': '192.168.30.5', 'path': '/'} for k,v in cookie_dict.items()])
        page = await context.new_page()
        
        await page.goto(f'{url}/')
        await page.wait_for_timeout(2000)
        
        js_code = f"""async () => {{
            let r = await fetch('{url}/getModules', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'token': '{token}'
                }},
                body: JSON.stringify({{"onuLightInfo": {{"slotNumber": -1, "ponPort": -1, "sn": ""}}}})
            }});
            return await r.text();
        }}"""
        res = await page.evaluate(js_code)
        print('Result 1:', res[:200])

        js_code2 = f"""async () => {{
            let r = await fetch('{url}/getModules', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'token': '{token}'
                }},
                body: JSON.stringify({{"onuLightInfo": {{"pageNum": 1, "pageSize": 100, "slotNumber": -1, "ponPort": -1, "sn": ""}}}})
            }});
            return await r.text();
        }}"""
        res2 = await page.evaluate(js_code2)
        print('Result 2:', res2[:200])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
