import asyncio
import sys
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_req(req):
            if req.method == 'POST':
                print(f'REQ: {req.url}')
                try: print(f'DATA: {req.post_data}')
                except: pass
                
        async def handle_res(res):
            if 'getModules' in res.url or 'setModules' in res.url:
                try: print(f'RES: {await res.text()}')
                except: pass

        page.on('request', handle_req)
        page.on('response', handle_res)
        
        print('Navigating...')
        await page.goto('http://103.157.79.178:8002/')
        await page.wait_for_timeout(3000)
        
        print('Filling form...')
        await page.evaluate('''() => {
            const inputs = document.querySelectorAll('input');
            for(let inp of inputs) {
                if(inp.type === 'password') { inp.value = 'ggclink0lt'; }
                else if(inp.type === 'text') { inp.value = 'root'; }
                inp.dispatchEvent(new Event('input', { bubbles: true }));
            }
            const btn = document.querySelector('.login__content__form__btn button') || document.querySelector('button');
            if(btn) btn.click();
        }''')
        
        await page.wait_for_timeout(4000)
        await page.screenshot(path='playwright_login_test.png', full_page=True)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
