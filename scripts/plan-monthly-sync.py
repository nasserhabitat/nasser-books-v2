"""Produce a read-only, ID-preserving monthly update plan from metadata."""
import json
from pathlib import Path,PureWindowsPath
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
read=lambda name:json.loads((ROOT/'scripts'/name).read_text(encoding='utf-8-sig'))
inventory=read('monthly-sync-local-inventory.json')
cloud=read('monthly-sync-cloud-inventory.json')['files']
legacy=read('monthly-sync-legacy-folders.json')
cat=json.loads((ROOT/'ai-index.json').read_text(encoding='utf-8'))['books']
work=next(x for x in inventory if x['root'].startswith('C:'))
drive_roots=[x for x in inventory if x['root'].startswith('G:')]
work_by_path={f['relative'].casefold():f for f in work['files']}
cloud_by_id={f['drive_id']:f for f in cloud}
memberships={file_id:row for row in legacy for file_id in row['file_ids']}
rows=[]
for b in cat:
 for lang in ('ar','en'):
  for fmt,key in [('docx','docx'),('pdf','pdf_external')]:
   name=f'{b["book_number"]}-{b["id"]}-{lang}.{fmt}'
   relative=f'{b["book_number"]}-{b["id"]}\\{lang}\\{name}'
   src=work_by_path.get(relative.casefold())
   url=b[lang].get(key,'').strip()
   file_id=url.split('id=',1)[1].split('&',1)[0] if 'id=' in url else None
   target=cloud_by_id.get(file_id)
   issues=[];local_matches=[]
   if src is None:issues.append('missing_working_source')
   if file_id is None:issues.append('no_drive_id_in_catalogue')
   elif not target or not target['accessible']:issues.append('drive_object_not_accessible')
   if target and target['accessible']:
    editions={(u['number'],u['lang']) for u in target['uses']}
    if len(editions)>1:issues.append('id_reused_across_editions_no_write')
    if not target['public']:issues.append('public_sharing_requires_author_approval')
    expected='application/pdf' if fmt=='pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    if target['mime_type']!=expected:issues.append('mime_type_mismatch')
    owner=memberships.get(file_id)
    if b['book_number']<=69 and (not owner or owner['number']!=b['book_number'] or owner['language']!=lang):issues.append('original_folder_identity_mismatch')
    for root in drive_roots:
     for f in root['files']:
      if f['name']==target['name'] and f['extension']=='.'+fmt and (target['bytes'] is None or target['bytes']==f['bytes']):
       # Old content.docx names repeat; require the verified legacy folder.
       if owner and root['root'].endswith('كتبي'):
        parts=PureWindowsPath(f['relative']).parts
        if len(parts)<3 or parts[0].casefold()!=owner['id'].casefold() or parts[1]!=owner['language']:continue
       elif owner:continue
       local_matches.append(str(PureWindowsPath(root['root'])/f['relative']))
   hard={'missing_working_source','drive_object_not_accessible','id_reused_across_editions_no_write','mime_type_mismatch','original_folder_identity_mismatch'}
   action='review_before_any_update' if hard.intersection(issues) else 'new_upload_only_after_approval' if not file_id else 'compare_content_then_update_existing_id'
   rows.append({'number':b['book_number'],'id':b['id'],'language':lang,'format':fmt,'working_file':str(PureWindowsPath(work['root'])/relative),'source_exists':src is not None,'drive_id':file_id,'drive_url':url or None,'drive_name':target['name'] if target else None,'current_drive_local_matches':local_matches,'intended_drive_path':str(PureWindowsPath(r'G:\Mon Drive\كتبي')/f'{b["book_number"]}-{b["id"]}'/lang/name),'source_bytes':src['bytes'] if src else None,'drive_bytes':target['bytes'] if target else None,'same_size_only':src['bytes']==target['bytes'] if src and target and target['bytes'] is not None else None,'issues':issues,'planned_action':action})
duplicates=[]
mirror=next(x for x in inventory if x['root']==r'G:\Mon Drive\google_books')
for f in mirror['files']:
 local=work_by_path.get(f['relative'].casefold())
 if local:duplicates.append({'relative':f['relative'],'same_size_only':local['bytes']==f['bytes']})
summary={'books':112,'language_editions':224,'word_pdf_pairs':len(rows),'linked_file_references':sum(bool(r['drive_id']) for r in rows),'unique_linked_objects':len(cloud),'drive_readable_objects':sum(x['accessible'] for x in cloud),'inaccessible_objects':sum(not x['accessible'] for x in cloud),'non_public_objects':sum(x['accessible'] and not x['public'] for x in cloud),'ids_shared_across_editions':sum(len({(u['number'],u['lang']) for u in x['uses']})>1 for x in cloud),'missing_working_word':sum(r['format']=='docx' and not r['source_exists'] for r in rows),'missing_working_pdf':sum(r['format']=='pdf' and not r['source_exists'] for r in rows),'missing_new_word_ids':sum(r['number']>=70 and r['format']=='docx' and not r['drive_id'] for r in rows),'missing_new_pdf_ids':sum(r['number']>=70 and r['format']=='pdf' and not r['drive_id'] for r in rows),'mirrored_files_compared':len(duplicates),'mirrored_same_size_only':sum(x['same_size_only'] for x in duplicates),'mirrored_different_size':sum(not x['same_size_only'] for x in duplicates),'planned_actions':dict(Counter(r['planned_action'] for r in rows))}
result={'checked_at':'2026-10-03','mode':'read_only_plan_no_drive_writes','summary':summary,'limitations':['Sizes and dates are not proof of identical text or of the latest authorial edition.','No book content was downloaded from Drive; no content hashes compared.','No sharing, file names, folders, bytes, or site links were changed by this inspection.','Copies in Drive google_books have different IDs; they cannot replace original linked objects automatically.'],'rows':rows,'drive_google_books_comparison':duplicates}
(ROOT/'scripts/monthly-sync-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
