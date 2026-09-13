const fs=require('node:fs'),cp=require('node:child_process');
const files=cp.execFileSync('git',['ls-files','books/*/*/index.html'],{encoding:'utf8'}).trim().split('\n');
for(const file of files){
 const old=fs.readFileSync(file,'utf8');
 const next=old.replace(/https:\/\/creativecommons.org\/licenses\/by-nc(?:-nd|-sa)?\/4\.0\//g,'https://creativecommons.org/licenses/by-sa/4.0/')
 .replace(/Attribution-NonCommercial-NoDerivatives/g,'Attribution-ShareAlike')
 .replace(/CC BY-NC-ND 4\.0/g,'CC BY-SA 4.0')
 .replace(/All Rights Reserved/gi,'CC BY-SA 4.0')
 .replace(/جميع الحقوق محفوظة/g,'الكتب متاحة بترخيص CC BY-SA 4.0');
 if(next!==old)fs.writeFileSync(file,next);
 if(next.includes('by-nc'))throw Error(file);
}
console.log('Verified license URLs on '+files.length+' pages');
