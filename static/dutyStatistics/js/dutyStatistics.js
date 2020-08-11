(function () {

    // 加载事件
    window.addEventListener('load', function (e) {

        // 一覧明細
        var changeList = $("tr[class^='row']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                    // 社員番号
                    var empNo = $(changeList[i]).find("th[class='field-empNo']").text()
                    // 社員番号編集リンクを削除する
                    $(changeList[i]).find("th[class='field-empNo']").find('a').remove();
                    // もとの表示内容を追加
                    $(changeList[i]).find("th[class='field-empNo']").html(empNo);
             }
        }

        // 導出ボタン
        $(".actions button[data-name='export']").click(function(){
            setTimeout("window.location.reload()",1000);
        });

    });
})();
