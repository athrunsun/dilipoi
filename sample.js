var vid="XMTQ0NDk1NDQ1Ng==";
var hd2="2";
var typ="youku";
var sign="80e7b435d42d25ec0915c85544c1a055";
//if (vid.substr(2,1)=="_"){
    if (vid.substr(2,1)=="_" && typ!="yun"){
        var vid = vid.split("_")[1];
    }
// if(typ=='_tudou'){ url=cl_m+hd2+vid+typ; } else{
    url='/parse.php?xmlurl=null&type='+typ+'&vid='+vid+'&hd='+(SwfCc ? 2 : 3)+'&sign='+sign+'&tmsign=b28dac78a7c0f1b9d50751bfdec974a5';
// }
// var flashvars={f:url,s:2,c:0,t:8,l:'/player/black.jpg',p:ck_p,o:138,loaded:'loadedHandler'};
var flashvars={f:url,s:2,c:0,p:ck_p,o:138,loaded:'loadedHandler'};
document.getElementById('yytf').style.display='none';
if(SwfCc){
    if (window.XMLHttpRequest) { var xhr=new XMLHttpRequest(); } else { var xhr=new ActiveXObject("Microsoft.XMLHTTP"); }
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            document.getElementById('cplayer').innerHTML='<video width="'+ck_a+'" height="'+ck_b+'" marginheight="0" marginwidth="0" autoplay="autoplay" contextmenu="false" controls="controls"><source src="'+ xhr.responseText +'"></video>';
        }
    }
    xhr.open("GET", '/parse.php?h5url=null&type='+typ+'&vid='+vid+'&hd='+hd2+'&sign='+sign+'&tmsign=b28dac78a7c0f1b9d50751bfdec974a5&ajax=1', true);
    xhr.send();
}
else{
    var params={bgcolor:'#FFF',allowFullScreen:true,allowScriptAccess:'always',wmode:'transparent'};
    CKobject.embedSWF('video.swf','cplayer','ckplayer_a1',ck_w,ck_h,flashvars,params);
}