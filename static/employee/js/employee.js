(function () {

    // 加载事件
    window.addEventListener('load', function (e) {
        // 該当ログインユーザーのIDを取得
        var userId = eval($("#userId").val());
        // 該当ログインユーザーの権限を取得
        var authPermission = eval($("#authPermission").val().toLowerCase());
        // changeListのログインユーザーのcolumnを隠す
        $(".column-user_id").hide()
        // changeListのログインユーザーのデータ記録を隠す
        $(".field-user_id").hide()

        // 一覧明細
        var changeList = $("tr[class^='row']");
        // 編集リンク削除・追加
        if (changeList) {
            for (i = 0; i < changeList.length; i++) {
                // 社員ID
                var user_id = $(changeList[i]).find("td[class='field-user_id']").text()
                // 社員名
                var empName = $(changeList[i]).find("th[class='field-name']").text()
                // ログインユーザーはスーパーユーザーではなく、ログインユーザー以外の社員名編集リンクを隠す
                if (!authPermission && (user_id != userId)){
                    // 社員名編集リンクを削除する
                    $(changeList[i]).find("th[class='field-name']").find('a').remove();
                    // もとの表示内容を追加
                    $(changeList[i]).find("th[class='field-name']").html(empName);
                }
             }
        }

        // 選択されている明細の申请状態より削除ボタンの活性化制御
        var btnCtrlFunc = function() {
            // 一覧明細
            var changeList = $("tr[class^='row']");
            // 社員ID
            var user_id = $(changeList[i]).find("td[class='field-user_id']").text()
            // 社員名
            var empName = $(changeList[i]).find("th[class='field-name']").text()
            // 削除ボタン
            var delBtn = $(".actions button[data-name='delete_selected']");
            // 削除ボタンを表示する
            if (delBtn) {
                delBtn.show();
            }
            if (changeList) {
                for (i = 0; i < changeList.length; i++) {
                    // 選択されているかを判断する
                    var selectedFlg = $(changeList[i]).find('tr').context.classList.contains('selected');
                    // 選択されている社員ID
                    var user_id = $(changeList[i]).find("td[class='field-user_id']").text()
                    // ログインユーザーはスーパーユーザーではなく、本人以外のユーザーがチェックされる時、削除ボタンを隠す
                    if (!authPermission && selectedFlg && (user_id != userId)){
                        // 削除ボタンを隠す
                        if (delBtn) {
                            delBtn.hide();
                        }
                    }
                 }
            }
        }

        // 明細一覧のチェックボックスのイベント
        $(".action-checkbox").bind('click', function(e){
            // 削除ボタンまたは取消ボタンの制御
            btnCtrlFunc();
        });

        // 一覧ヘッダ部のチェックボックスのイベント
        $(".action-checkbox-column").bind('click', function(e){
            // 削除ボタンまたは取消ボタンの制御
            btnCtrlFunc();
        });

    });
})();