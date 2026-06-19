import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept network requests
        async def handle_request(request):
            if '/getModules' in request.url and request.method == 'POST':
                try:
                    post_data = request.post_data
                    print(f'API Call to getModules. Payload: {post_data}')
                except:
                    pass
        
        page.on('request', handle_request)
        
        print('Navigating to login...')
        await page.goto('http://192.168.30.3:8001/login.html')
        await page.fill('input[type="text"]', 'root')
        await page.fill('input[type="password"]', '#eugine0909')
        print('Clicking login...')
        # Just click the first primary button (usually login)
        await page.evaluate('document.querySelector(".el-button--primary").click()')
        
        await asyncio.sleep(5)
        print('Waiting 10s to capture background requests for Authorized List...')
        await asyncio.sleep(10)
        
        await browser.close()

asyncio.run(main())
