const p = require("puppeteer");
const U = "http://127.0.0.1:9222";
const C = "https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215";
function s(m){return new Promise(r=>setTimeout(r,m))}

(async()=>{
  const b=await p.connect({browserURL:U});
  const pages=await b.pages();
  console.log(`共 ${pages.length} 个标签页`);
  
  for(const pg of pages){
    const url=pg.url();
    console.log(`  URL: ${url.substring(0,120)}`);
    console.log(`  标题: ${await pg.title()}`);
  }
  
  // 找U校园页面
  let pg = pages[0];
  for(const p of pages){
    const u=p.url();
    if(u.includes('unipus')||u.includes('ucloud')){
      pg=p; break;
    }
  }
  
  console.log(`\n使用页面: ${pg.url().substring(0,100)}`);
  
  // 如果空白，重新导航
  if(pg.url()==='about:blank'){
    console.log("\n页面空白，重新导航...");
    await pg.goto(C,{waitUntil:'domcontentloaded',timeout:30000}).catch(()=>{});
    await s(8000);
    
    // 等待课程树
    for(let i=0;i<20;i++){
      const n=await pg.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);
      if(n>0){console.log(`课程树已加载: ${n}个任务`);break}
      await s(1000);
    }
  }
  
  // 获取课程信息
  const info = await pg.evaluate(()=>{
    const url = window.location.href;
    // 提取所有标题级文本
    const getTexts = (sel)=>{
      const els = document.querySelectorAll(sel);
      return Array.from(els).filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).filter(t=>t.length>0);
    };
    
    // 找"切换教程"或类似选择器内容
    const switcher = document.querySelector('[class*="switch"],[class*="select"],[class*="picker"]');
    
    // 找ant design tabs
    const tabs = document.querySelectorAll('.ant-tabs-tab');
    const tabTexts = Array.from(tabs).filter(t=>t.offsetParent!==null).map(t=>t.innerText.trim());
    
    // 页面body主要文本
    const bodyText = document.body.innerText.substring(0,3000);
    
    // 看URL里有没有unit参数
    const urlParams = new URLSearchParams(url.split('?')[1]||'');
    
    return {
      url,
      urlParams: Object.fromEntries(urlParams),
      tabTexts,
      bodyText: bodyText.substring(0,2000),
      hasSwitcher: !!switcher,
      switcherText: switcher?.innerText?.trim()
    };
  });
  
  console.log("\n=== 当前课程信息 ===");
  console.log("URL:", info.url);
  console.log("\n-- 页面主体(前2000字) --");
  console.log(info.bodyText);
  if(info.tabTexts.length>0) console.log("\n-- Tab --", info.tabTexts);
  
  await b.disconnect();
})().catch(e=>console.error("❌",e.message));
