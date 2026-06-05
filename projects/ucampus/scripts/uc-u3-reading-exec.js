/** Reading Prac 执行 + 继续 */
const puppeteer = require('puppeteer');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await puppeteer.connect({browserURL:'http://127.0.0.1:9222'});
  const [p] = await b.pages();
  await sleep(1000);

  const answers=[0,3,1,3,2];
  await p.evaluate((ans)=>{
    const qs=document.querySelectorAll('.question-common-abs-choice');
    qs.forEach((q,qi)=>{
      const opts=q.querySelectorAll('.option.isNotReview');
      const idx=qi<ans.length?ans[qi]:0;
      if(idx<opts.length){opts[idx].scrollIntoView({block:'center'});opts[idx].click();}
    });
  },answers);
  await sleep(500);

  await p.evaluate(()=>{
    const btn=document.querySelector('a.btn');
    if(btn){
      const keys=Object.keys(btn);const pk=keys.find(k=>k.startsWith('__reactProps'));
      if(pk&&btn[pk]?.onClick)btn[pk].onClick({preventDefault(){},stopPropagation(){},target:btn,currentTarget:btn});
      btn.click();btn.dispatchEvent(new MouseEvent('mousedown',{bubbles:true}));btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));
    }
  });
  await sleep(8000);

  const r=await p.evaluate(()=>{
    const t=document.body.innerText||'';
    return{pass:t.includes('答题小结')&&!t.includes('没有达到闯关条件'),corr:(t.match(/正确\s*\((\d+)\/(\d+)\)/)||['','0'])[1],cont:t.includes('继续学习')};
  });
  console.log(`Reading Prac: ${r.corr}/5 通过=${r.pass}`);

  if(r.cont){
    await p.evaluate(()=>{for(const btn of document.querySelectorAll('a.btn')){if(btn.innerText.trim().includes('继续学')){btn.click();btn.dispatchEvent(new MouseEvent('click',{bubbles:true}));break;}}});
    await sleep(6000);
    console.log('导航:',await p.evaluate(()=>({url:window.location.href,text:(document.body.innerText||'').substring(0,200)})));
  }

  await b.disconnect();
})();
