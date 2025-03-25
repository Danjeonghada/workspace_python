$(document).ready(function(){
    $(document).on('click', 'tr', function(){
        alert($(this).find('td').eq(2).text());
        let code = $(this).find('td').eq(2).text();
        let subUrl = 'http://127.0.0.1:5500/main'
        $.ajax({
            url : subUrl
           ,type : 'POST'
           ,data : JSON.stringify({'market':code})
           ,contentType : 'application/json'
           ,dataType : 'json'
           ,success : function(res){
                console.log(res);
           },
           error : function(e){
                console.log(e);
           }
        });
    });
});