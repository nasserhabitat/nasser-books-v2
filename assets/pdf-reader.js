/* Public Drive PDFs only; no binary books are hosted in GitHub. */
(() => {
  'use strict';
  const script = document.currentScript;
  const dataUrl = new URL('pdf-reader-catalog.json', script.src);
  const messages = {
    ar: { title:'قراءة PDF داخل الموقع', load:'عرض PDF هنا', open:'فتح PDF في Google Drive', note:'يُحمّل العارض عند الضغط فقط. إذا لم يعمل التضمين، افتح الملف في Google Drive.', pending:'ملف PDF لهذه النسخة لم يُربط على Google Drive بعد.', private:'ملف PDF يحتاج إتاحة القراءة العامة قبل عرضه للزوار.', review:'رابط PDF يحتاج مراجعة مطابقته للكتاب واللغة؛ لم نعرض ملفًا قد يكون لكتاب آخر.', unavailable:'تعذّر التحقق من ملف PDF الحالي؛ القراءة النصية ما زالت متاحة.', error:'تعذّر تحميل بيانات العارض. أعد تحميل الصفحة أو استخدم روابط الكتاب الأخرى.', loading:'جارٍ تحميل عارض Google Drive…', select:'اختر الكتاب واللغة' },
    en: { title:'Read the PDF on this website', load:'Show PDF here', open:'Open PDF in Google Drive', note:'The viewer loads only when requested. If embedding fails, open the file in Google Drive.', pending:'This edition has no Google Drive PDF link yet.', private:'Public read access is required before this PDF can be displayed.', review:'The PDF link needs a book/language identity review. No potentially unrelated book is embedded.', unavailable:'The current PDF could not be verified. The text edition remains available.', error:'Could not load reader data. Reload the page or use the other book links.', loading:'Loading the Google Drive viewer…', select:'Choose a book and language' }
  };
  const element = (tag,text) => { const n=document.createElement(tag); if(text)n.textContent=text; return n; };
  function render(host,entry) {
    host.replaceChildren();
    const lang=entry.language==='en'?'en':'ar',t=messages[lang];
    host.dir=lang==='ar'?'rtl':'ltr'; host.lang=lang;
    host.append(element('h2',t.title),element('p',`${entry.number}. ${entry.title}`));
    const status=element('p');status.className='pdf-reader-status';status.setAttribute('role','status');host.append(status);
    if(entry.status!=='ready'||!/^[-\w]{16,120}$/.test(entry.drive_id||'')){status.textContent=t[entry.status]||t.review;return;}
    const actions=element('div');actions.className='pdf-reader-actions';
    const button=element('button',t.load);button.type='button';button.setAttribute('aria-expanded','false');
    const link=element('a',t.open);link.href=`https://drive.google.com/file/d/${entry.drive_id}/view`;link.target='_blank';link.rel='noopener noreferrer';
    actions.append(button,link);host.append(actions);
    const note=element('p',t.note);note.className='pdf-reader-note';host.append(note);
    button.addEventListener('click',()=>{
      if(host.querySelector('iframe'))return;
      const frame=element('iframe');frame.title=`PDF — ${entry.title} (${lang})`;frame.loading='lazy';frame.referrerPolicy='no-referrer';frame.allowFullscreen=true;
      frame.src=`https://drive.google.com/file/d/${entry.drive_id}/preview`;
      frame.addEventListener('load',()=>{status.textContent=t.note;},{once:true});
      host.append(frame);button.setAttribute('aria-expanded','true');button.disabled=true;status.textContent=t.loading;
    });
  }
  async function init() {
    const hosts=[...document.querySelectorAll('[data-pdf-reader]')];if(!hosts.length)return;
    try {
      const response=await fetch(dataUrl,{cache:'no-cache'});if(!response.ok)throw Error('Reader catalogue unavailable');const data=await response.json();
      for(const host of hosts){
        if(host.dataset.pdfReader==='library'){
          const t=messages.ar,label=element('label',t.select),select=element('select'),panel=element('div');select.id='pdf-edition-select';label.htmlFor=select.id;
          for(const entry of data.editions){const option=element('option',`${entry.number}. ${entry.title} — ${entry.language==='ar'?'العربية':'English'}${entry.status==='ready'?'':' · PDF غير متاح حاليًا'}`);option.value=`${entry.book_id}/${entry.language}`;select.append(option);}
          const params=new URLSearchParams(location.search),requested=`${params.get('book')||''}/${params.get('lang')||'ar'}`;
          select.value=data.editions.some(e=>`${e.book_id}/${e.language}`===requested)?requested:`${(data.editions.find(e=>e.status==='ready')||data.editions[0]).book_id}/${(data.editions.find(e=>e.status==='ready')||data.editions[0]).language}`;
          host.replaceChildren(label,select,panel);
          const show=()=>{const entry=data.editions.find(e=>`${e.book_id}/${e.language}`===select.value);if(entry)render(panel,entry);};select.addEventListener('change',show);show();
        }else{
          const entry=data.editions.find(e=>e.book_id===host.dataset.bookId&&e.language===host.dataset.language);if(entry)render(host,entry);
        }
      }
    }catch(error){for(const host of hosts){host.append(element('p',messages[host.dataset.language==='en'?'en':'ar'].error));}}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
