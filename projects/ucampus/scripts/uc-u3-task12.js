/** Task 1 + Task 2 快速 */
const puppeteer = require('puppeteer');
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function fillAndSubmit(p, ans){
  await p.evaluate((a)=>{
    const tas=document.querySelectorAll('textarea');
    const ns=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
    tas.forEach((ta,i)=>{if(i<a.length){ns.call(ta,a[i]);ta.dispatchEvent(new Event('input',{bubbles:true}));}});
  },ans);
  await sleep(300);
  await p.evaluate(()=>{const btn=document.querySelector('a.btn');if(btn){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
  await sleep(8000);
  const r=await p.evaluate(()=>{const t=document.body.innerText||'';return{pass:t.includes('答题小结'),cont:t.includes('继续学习')};});
  return r;
}

(async()=>{
  const b=await puppeteer.connect({browserURL:'http://127.0.0.1:9222'});
  const[p]=await b.pages();
  await sleep(2000);

  // Task 1
  const ans1=[
    'The 20th century witnessed the invention of infection-fighting drugs that have saved millions of lives, and penicillin is one of these drugs.',
    'The past few years have seen a rise in the number of smart homes, with appliances and accessories all connected through Wi-Fi and controlled with the touch of a finger or the sound of your voice.',
    'The last decades have witnessed China\'s transformation from an underdeveloped country into the world\'s second-largest economy.'
  ];
  let r=await fillAndSubmit(p, ans1);
  console.log(`Task1: pass=${r.pass}, cont=${r.cont}`);

  if(r.cont){
    await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('继续学')){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));break;}}});
    await sleep(6000);
    const nav=await p.evaluate(()=>({url:window.location.href,text:(document.body.innerText||'').substring(0,200)}));
    console.log('Task2:', JSON.stringify(nav));
    
    // Task 2 will be translation
    if(nav.text.includes('translate')||nav.text.includes('翻译')){
      const t2text=await p.evaluate(()=>(document.body.innerText||'').substring(0,1500));
      console.log(t2text);
      const tas=await p.evaluate(()=>document.querySelectorAll('textarea').length);
      if(tas>0){
        const ans2=['Three years witnessed the rapid growth of the company from a small startup to a well-known brand.','The past decade has seen remarkable progress in artificial intelligence technology.'];
        r=await fillAndSubmit(p, ans2);
        console.log(`Task2: pass=${r.pass}`);
        if(r.cont){
          await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('继续学')){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));break;}}});
          await sleep(6000);
          console.log('Collo:',await p.evaluate(()=>({url:window.location.href,text:(document.body.innerText||'').substring(0,200)})));
        }
      }
    }
  }

  // Final status
  await p.goto('https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215',{waitUntil:'domcontentloaded'}).catch(()=>{});
  await sleep(5000);
  for(let i=0;i<20;i++){const n=await p.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);if(n>5)break;await sleep(1000);}
  await p.evaluate(()=>{const tabs=document.querySelectorAll('[class*="unitTabItemContainer"]');for(const tab of tabs){if(tab.innerText.trim()==='Unit 3'){tab.click();return;}}});
  await sleep(4000);
  for(let i=0;i<20;i++){const n=await p.evaluate(()=>document.querySelectorAll('[class*="taskItemInnerLayout"]').length);if(n>5)break;await sleep(1000);}
  await p.evaluate(()=>{document.querySelectorAll('.ant-collapse-header').forEach(h=>{const parent=h.closest('.ant-collapse-item');if(parent&&!parent.classList.contains('ant-collapse-item-active'))h.click();});});

  const tasks=await p.evaluate(()=>{
    const items=document.querySelectorAll('[class*="taskItemInnerLayout"]');
    const r=[];for(const item of items){if(item.offsetParent===null)continue;const ne=item.querySelector('[class*="taskTypeName"]');const se=item.querySelector('[class*="nodePassStateTip"]');if(ne&&se)r.push({name:ne.innerText.trim(),status:se.innerText.trim()});}return r;
  });
  const us=tasks.filter(x=>x.status==='未开始');
  const co=tasks.filter(x=>x.status==='已完成');
  console.log(`\n📊 U3: ${co.length}完成, ${us.length}未开始`);
  us.forEach(x=>console.log(`  剩余: ${x.name}`));

  await b.disconnect();
})();
