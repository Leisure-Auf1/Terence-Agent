/** Expressions retry */
const puppeteer = require('puppeteer');
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function fillSubmit(p, ans, label) {
  await p.evaluate((a)=>{
    const ns=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
    for(let i=0;i<a.length;i++){
      const blank=document.querySelector(`[data-rbd-droppable-id="${i}"]`);
      if(blank){const inp=blank.querySelector('input');
        if(inp){ns.call(inp,a[i]);inp.dispatchEvent(new Event('input',{bubbles:true}));}
      }
    }
  },ans);
  await sleep(300);
  await p.evaluate(()=>{const btn=document.querySelector('a.btn');if(btn){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
  await sleep(8000);
  const r=await p.evaluate(()=>{const t=document.body.innerText||'';return{pass:t.includes('答题小结')&&!t.includes('没有达到闯关条件'),corr:(t.match(/正确\s*\((\d+)\/(\d+)\)/)||['','0'])[1],cont:t.includes('继续学习')};});
  console.log(`${label}: ${r.corr}/10 pass=${r.pass}`);
  return r;
}

(async()=>{
  const b=await puppeteer.connect({browserURL:'http://127.0.0.1:9222'});
  const[p]=await b.pages();
  await sleep(1000);

  const tries=[
    { ans:['seal the deal','has an impact on','specializes in','are incorporated into','took','approach to','was singled out','charged into','diverting'], label:'Try1: merged incorp' },
    { ans:['seal the deal','has an impact on','specializes in','are incorporated','into','took a','approach to','was singled out','charged into','diverting'], label:'Try2: took a' },
    { ans:['seal the deal','impacts on','specializes in','are incorporated into','took','approach to','was singled out','charged into','diverting'], label:'Try3: impacts on' },
  ];

  for(let i=0;i<tries.length;i++){
    const r=await fillSubmit(p, tries[i].ans, tries[i].label);
    if(r.pass||r.cont){break;}
    if(r.corr!=='0'&&i<tries.length-1){
      await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('返回修改')){btn.click();break;}}});
      await sleep(4000);
    }
  }

  // Check next status
  const r=await p.evaluate(()=>{const t=document.body.innerText||'';return{pass:t.includes('答题小结')&&!t.includes('没有达到闯关条件'),cont:t.includes('继续学习')};});
  if(r.cont){
    await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('继续学')){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));break;}}});
    await sleep(6000);
    console.log('导航:',await p.evaluate(()=>({url:window.location.href,text:(document.body.innerText||'').substring(0,200)})));
  }

  await b.disconnect();
})();
