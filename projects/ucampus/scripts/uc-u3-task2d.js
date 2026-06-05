/** Task 2 - 带逗号版本 */
const puppeteer = require('puppeteer');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async()=>{
  const b=await puppeteer.connect({browserURL:'http://127.0.0.1:9222'});
  const[p]=await b.pages();

  // Task 2 should still be showing on the page. Check and enter.
  await p.goto('https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215',{waitUntil:'domcontentloaded'}).catch(()=>{});
  await sleep(5000);
  for(let i=0;i<20;i++){const n=await p.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);if(n>5)break;await sleep(1000);}
  await p.evaluate(()=>{const tabs=document.querySelectorAll('[class*="unitTabItemContainer"]');for(const tab of tabs){if(tab.innerText.trim()==='Unit 3'){tab.click();return;}}});
  await sleep(4000);
  for(let i=0;i<20;i++){const n=await p.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);if(n>5)break;await sleep(1000);}
  await p.evaluate(()=>{document.querySelectorAll('.ant-collapse-header').forEach(h=>{const parent=h.closest('.ant-collapse-item');if(parent&&!parent.classList.contains('ant-collapse-item-active'))h.click();});});

  // Enter Task 2
  await p.evaluate(()=>{
    const items=document.querySelectorAll('[class*="taskItemInnerLayout"]');
    for(const item of items){if(item.offsetParent===null)continue;const ne=item.querySelector('[class*="taskTypeName"]');const se=item.querySelector('[class*="nodePassStateTip"]');if(ne&&ne.innerText.trim()==='Task 2'&&se&&se.innerText.trim()==='未开始'){item.scrollIntoView({block:'center'});const keys=Object.keys(item);const pk=keys.find(k=>k.startsWith('__reactProps'));if(pk&&item[pk]?.onClick)item[pk].onClick({preventDefault(){},stopPropagation(){}});item.click();return;}}
  });
  await sleep(8000);
  await p.evaluate(()=>{document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask').forEach(m=>m.style.display='none');for(const b of document.querySelectorAll('button')){const t=b.innerText.trim();if((t==='我知道了'||t.includes('知道')||t==='确 定')&&b.offsetParent!==null){b.click();}}});

  // Try with commas
  const ans=[
    'Had it not been for the firm economic reforms and opening-up,',
    'Had the weather been good when you came last year,',
    'Had he given more thought to the color of the fence,'
  ];
  await p.evaluate((a)=>{
    const tas=document.querySelectorAll('textarea');
    const ns=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
    tas.forEach((ta,i)=>{if(i<a.length){ns.call(ta,a[i]);ta.dispatchEvent(new Event('input',{bubbles:true}));ta.dispatchEvent(new Event('change',{bubbles:true}));}});
  },ans);
  await sleep(300);

  await p.evaluate(()=>{const btn=document.querySelector('a.btn');if(btn){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
  await sleep(8000);

  const r=await p.evaluate(()=>{const t=document.body.innerText||'';return{pass:t.includes('答题小结'),cont:t.includes('继续学习'),text:t.substring(0,300)};});
  console.log(`Task2: pass=${r.pass} cont=${r.cont}`);
  console.log(r.text);

  if(r.cont){
    await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('继续学')){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));break;}}});
    await sleep(6000);
    console.log('导航:',await p.evaluate(()=>({url:window.location.href,text:(document.body.innerText||'').substring(0,200)})));
  }

  await b.disconnect();
})();
