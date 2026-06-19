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
        # Create context with the extracted cookie
        cookies = []
        for k, v in cookie_dict.items():
            cookies.append({'name': k, 'value': v, 'domain': '192.168.30.5', 'path': '/'})
        context = await browser.new_context()
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        async def handle_req(req):
            if 'getModules' in req.url:
                try: print(f'REQ POST DATA: {req.post_data}')
                except: pass
                
        page.on('request', handle_req)
        
        # Navigate directly to the index after login
        await page.goto(f'{url}/')
        
        # Wait for page to load
        await page.wait_for_timeout(3000)
        
        # Evaluate to set the token in local storage if needed
        await page.evaluate(f'localStorage.setItem(\"token\", \"{token}\")')
        await page.evaluate(f'sessionStorage.setItem(\"token\", \"{token}\")')
        await page.reload()
        await page.wait_for_timeout(5000)
        
        # click menu PON
        print("Clicking menu...")
        await page.evaluate('''() => {
            let menus = document.querySelectorAll('.v-menu__title');
            for(let m of menus) {
                if(m.innerText.includes('PON')) {
                    m.click();
                }
            }
        }''')
        await page.wait_for_timeout(2000)
        
        await page.evaluate('''() => {
            let menus = document.querySelectorAll('.v-menu__item');
            for(let m of menus) {
                if(m.innerText.includes('ONU')) {
                    m.click();
                }
            }
        }''')
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path='after_login_with_cookie.png')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
